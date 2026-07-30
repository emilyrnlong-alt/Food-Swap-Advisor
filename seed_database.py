"""
seed_database.py
-----------------
Populates foodswap.db from data/foods.csv and data/substitutions.csv.

Run this once before first launching the app:
    python seed_database.py

It is idempotent-ish: if the DB already has foods in it, it asks before
wiping and reloading, so you don't accidentally lose collected votes.
"""

import csv
import sys
from pathlib import Path

import database

DATA_DIR = Path(__file__).parent / "data"


def load_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def seed(force: bool = False) -> None:
    database.init_db()

    if database.is_seeded() and not force:
        answer = input(
            "Database already has data. Reseeding will WIPE existing votes. "
            "Continue? [y/N] "
        )
        if answer.strip().lower() != "y":
            print("Aborted. No changes made.")
            return

    with database.get_connection() as conn:
        conn.execute("DELETE FROM substitutions")
        conn.execute("DELETE FROM foods")

        foods = load_csv(DATA_DIR / "foods.csv")
        conn.executemany(
            """INSERT INTO foods
               (food_id, name, category, calories, fiber_g, sugar_g, protein_g, sodium_mg, carbs_g)
               VALUES (:food_id, :name, :category, :calories, :fiber_g, :sugar_g, :protein_g, :sodium_mg, :carbs_g)""",
            foods,
        )

        subs = load_csv(DATA_DIR / "substitutions.csv")
        conn.executemany(
            """INSERT INTO substitutions
               (sub_id, original_food_id, substitute_food_id, base_certainty, rationale)
               VALUES (:sub_id, :original_food_id, :substitute_food_id, :base_certainty, :rationale)""",
            subs,
        )

    print(f"Seeded {database.food_count()} foods and {database.substitution_count()} substitution links.")


if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    seed(force=force_flag)
