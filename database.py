"""
database.py
------------
SQLite data-access layer for the Food Swap Advisor app.

Design notes (kept here so the reasoning is visible on GitHub):

* Two tables: `foods` (nutrition facts per 100g) and `substitutions`
  (an edge table linking an "original" food to a healthier "substitute"
  food, plus vote counters).
* Certainty shown to the user is NOT just the raw upvote ratio. A brand
  new substitution with 1 upvote and 0 downvotes would otherwise show
  100% confidence, which is misleading. Instead we treat the curator's
  `base_certainty` as a prior belief worth PRIOR_WEIGHT pseudo-votes and
  blend it with the real votes -- this is the same idea behind a
  "Bayesian average" / IMDB-style weighted rating. See
  `voting.compute_certainty` for the actual formula.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent / "foodswap.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS foods (
    food_id     INTEGER PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    category    TEXT NOT NULL,
    calories    REAL NOT NULL,
    fiber_g     REAL NOT NULL,
    sugar_g     REAL NOT NULL,
    protein_g   REAL NOT NULL,
    sodium_mg   REAL NOT NULL,
    carbs_g     REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS substitutions (
    sub_id              INTEGER PRIMARY KEY,
    original_food_id    INTEGER NOT NULL REFERENCES foods(food_id),
    substitute_food_id  INTEGER NOT NULL REFERENCES foods(food_id),
    base_certainty      REAL NOT NULL,   -- curator's starting confidence, 0-100
    rationale           TEXT,
    upvotes             INTEGER NOT NULL DEFAULT 0,
    downvotes           INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_sub_original ON substitutions(original_food_id);
"""


@contextmanager
def get_connection():
    """Yield a SQLite connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Create tables if they don't already exist. Safe to call every app start."""
    with get_connection() as conn:
        conn.executescript(SCHEMA)


def is_seeded() -> bool:
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) AS n FROM foods").fetchone()
        return row["n"] > 0


def search_foods(query: str, limit: int = 15) -> list[sqlite3.Row]:
    """Case-insensitive substring search over food names, used for the
    autocomplete-style input box in the Streamlit UI."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM foods WHERE name LIKE ? ORDER BY name LIMIT ?",
            (f"%{query}%", limit),
        ).fetchall()
        return rows


def get_all_food_names() -> list[str]:
    with get_connection() as conn:
        rows = conn.execute("SELECT name FROM foods ORDER BY name").fetchall()
        return [r["name"] for r in rows]


def get_food_by_name(name: str) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM foods WHERE name = ?", (name,)).fetchone()


def get_food_by_id(food_id: int) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM foods WHERE food_id = ?", (food_id,)).fetchone()


def get_substitutions_for(food_id: int) -> list[sqlite3.Row]:
    """All substitution edges where `food_id` is the *original* (less healthy) food."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT s.*, f.name AS substitute_name, f.category AS substitute_category,
                   f.calories AS substitute_calories, f.fiber_g AS substitute_fiber_g,
                   f.sugar_g AS substitute_sugar_g, f.protein_g AS substitute_protein_g,
                   f.sodium_mg AS substitute_sodium_mg, f.carbs_g AS substitute_carbs_g
            FROM substitutions s
            JOIN foods f ON f.food_id = s.substitute_food_id
            WHERE s.original_food_id = ?
            """,
            (food_id,),
        ).fetchall()
        return rows


def adjust_vote(sub_id: int, upvote_delta: int = 0, downvote_delta: int = 0) -> None:
    """Adjust the upvote/downvote counters by the given deltas (can be
    negative, e.g. -1 to revoke a previously cast vote). Counts are
    floored at 0 so a bug or double-click can't push them negative.

    Used for all three vote actions in the UI:
      - New vote:    adjust_vote(sub_id, upvote_delta=+1)
      - Revoke vote: adjust_vote(sub_id, upvote_delta=-1)
      - Switch vote: adjust_vote(sub_id, upvote_delta=+1, downvote_delta=-1)
    """
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE substitutions
            SET upvotes   = MAX(upvotes + ?, 0),
                downvotes = MAX(downvotes + ?, 0)
            WHERE sub_id = ?
            """,
            (upvote_delta, downvote_delta, sub_id),
        )


def get_vote_counts(sub_id: int) -> tuple[int, int]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT upvotes, downvotes FROM substitutions WHERE sub_id = ?", (sub_id,)
        ).fetchone()
        return (row["upvotes"], row["downvotes"]) if row else (0, 0)


def food_count() -> int:
    with get_connection() as conn:
        return conn.execute("SELECT COUNT(*) AS n FROM foods").fetchone()["n"]


def substitution_count() -> int:
    with get_connection() as conn:
        return conn.execute("SELECT COUNT(*) AS n FROM substitutions").fetchone()["n"]
