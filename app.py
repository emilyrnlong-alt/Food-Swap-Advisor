"""
app.py
------
Streamlit front-end for the Food Swap Advisor.

Flow:
  1. User types/selects a food they eat.
  2. We look up its nutrition facts and any curated healthier substitutes.
  3. Each substitute is shown as a nutrition-facts-style comparison card,
     with a "% certainty this is healthier" badge.
  4. Upvote / downvote buttons feed back into `voting.compute_certainty`,
     so the badge shown to the *next* person shifts with community input.
"""

import streamlit as st

import database
from voting import compute_certainty, certainty_label

st.set_page_config(
    page_title="Food Swap Advisor",
    page_icon="🥗",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Styling -- a "nutrition facts label" inspired look: black/white/yellow,
# bold rules, monospace numerals, instead of a generic blue Streamlit theme.
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FAFAF7;
    }
    h1, h2, h3 {
        font-family: "Helvetica Neue", Arial, sans-serif;
        letter-spacing: -0.5px;
    }
    .facts-card {
        border: 3px solid #111111;
        border-radius: 2px;
        padding: 18px 20px;
        margin-bottom: 14px;
        background-color: #FFFFFF;
    }
    .facts-title {
        font-size: 1.05rem;
        font-weight: 800;
        text-transform: uppercase;
        border-bottom: 8px solid #111111;
        padding-bottom: 6px;
        margin-bottom: 8px;
    }
    .facts-row {
        display: flex;
        justify-content: space-between;
        font-family: "Courier New", monospace;
        font-size: 0.95rem;
        border-bottom: 1px solid #cccccc;
        padding: 3px 0;
    }
    .facts-row.better {
        color: #1B6B3A;
        font-weight: 700;
    }
    .facts-row.worse {
        color: #B3261E;
        font-weight: 700;
    }
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 700;
        color: white;
        margin-bottom: 6px;
    }
    .badge-high { background-color: #1B6B3A; }
    .badge-mod  { background-color: #C77800; }
    .badge-low  { background-color: #8A8A8A; }
    </style>
    """,
    unsafe_allow_html=True,
)

database.init_db()

# Tracks THIS browser session's own vote per substitution: sub_id -> "up" | "down" | None.
# Votes are anonymous (no accounts), so this only prevents a single session from
# double-voting or losing track of its own vote -- it doesn't stop a different
# session/browser from voting on the same swap. See README for this limitation.
if "my_votes" not in st.session_state:
    st.session_state.my_votes = {}

if not database.is_seeded():
    st.error(
        "The database hasn't been seeded yet. Run `python seed_database.py` "
        "in your terminal, then refresh this page."
    )
    st.stop()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🥗 Food Swap Advisor")
st.caption(
    f"Type a food you eat and get evidence-informed, healthier swaps — "
    f"backed by a {database.food_count()}-food nutrition database."
)

NUTRIENT_FIELDS = [
    ("calories", "Calories", "kcal", "lower"),
    ("fiber_g", "Fiber", "g", "higher"),
    ("sugar_g", "Sugar", "g", "lower"),
    ("protein_g", "Protein", "g", "higher"),
    ("sodium_mg", "Sodium", "mg", "lower"),
    ("carbs_g", "Carbs", "g", "lower"),
]


def render_facts_card(title: str, food_row, compare_to=None) -> None:
    """Render one nutrition-facts-style card as a SINGLE st.markdown() call.

    Important: each st.markdown() call is wrapped by Streamlit in its own
    isolated container. Opening a <div> in one call and closing it in a
    later call does NOT nest them in the real DOM -- the browser just
    closes the empty div immediately, which is why this used to render as
    a blank bordered box followed by unstyled text. Building the full
    card HTML as one string here fixes that.
    """
    rows_html = []
    for key, label, unit, better_direction in NUTRIENT_FIELDS:
        value = food_row[key]
        row_class = ""
        if compare_to is not None:
            base_value = compare_to[key]
            if value != base_value:
                improved = (value < base_value) if better_direction == "lower" else (value > base_value)
                row_class = "better" if improved else "worse"
        rows_html.append(
            f'<div class="facts-row {row_class}"><span>{label}</span>'
            f'<span>{value:g} {unit}</span></div>'
        )

    card_html = (
        f'<div class="facts-card">'
        f'<div class="facts-title">{title}</div>'
        f'{"".join(rows_html)}'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Food search / selection
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300)
def cached_food_names() -> list[str]:
    # Food names change rarely (only when the dataset is re-seeded), so we
    # cache this for 5 minutes instead of hitting SQLite on every keystroke.
    # Vote counts are NOT cached here since those need to update instantly.
    return database.get_all_food_names()


all_names = cached_food_names()

query = st.text_input("What food are you eating?", placeholder="e.g. potato chips, white bread, hot dog...")

selected_food_name = None
if query:
    matches = [n for n in all_names if query.lower() in n.lower()]
    if matches:
        selected_food_name = st.selectbox("Matching foods in our database:", matches)
    else:
        st.warning(
            "No matches in our database yet. Try a different search term, "
            "or browse the categories below."
        )

with st.expander("Or browse by category"):
    with database.get_connection() as conn:
        cats = [r["category"] for r in conn.execute("SELECT DISTINCT category FROM foods ORDER BY category")]
    picked_cat = st.selectbox("Category", cats, key="cat_picker")
    with database.get_connection() as conn:
        names_in_cat = [
            r["name"]
            for r in conn.execute(
                "SELECT name FROM foods WHERE category = ? ORDER BY name", (picked_cat,)
            )
        ]
    browsed = st.selectbox("Food", names_in_cat, key="food_picker")
    if st.button("Use this food"):
        selected_food_name = browsed

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
if selected_food_name:
    food = database.get_food_by_name(selected_food_name)
    st.divider()
    st.subheader(f"Your food: {food['name']}")
    render_facts_card(food["name"], food)

    subs = database.get_substitutions_for(food["food_id"])

    if not subs:
        st.info(
            "This food doesn't have a curated substitute in the database yet. "
            "It might already be a healthy choice, or it's on our list to add — "
            "see the README for how to contribute one."
        )
    else:
        st.subheader("Healthier swaps to try")
        # Rank substitutes by current certainty score, best first.
        scored = []
        for s in subs:
            certainty = compute_certainty(s["base_certainty"], s["upvotes"], s["downvotes"])
            scored.append((certainty, s))
        scored.sort(key=lambda pair: pair[0], reverse=True)

        for certainty, s in scored:
            label = certainty_label(certainty)
            badge_class = {"High confidence": "badge-high", "Moderate confidence": "badge-mod", "Low confidence": "badge-low"}[label]

            col1, col2 = st.columns([3, 2])
            with col1:
                st.markdown(
                    f'<span class="badge {badge_class}">{certainty}% certainty • {label}</span>',
                    unsafe_allow_html=True,
                )
                substitute_row = {
                    "calories": s["substitute_calories"],
                    "fiber_g": s["substitute_fiber_g"],
                    "sugar_g": s["substitute_sugar_g"],
                    "protein_g": s["substitute_protein_g"],
                    "sodium_mg": s["substitute_sodium_mg"],
                    "carbs_g": s["substitute_carbs_g"],
                }
                render_facts_card(f"Try instead: {s['substitute_name']}", substitute_row, compare_to=food)
                st.caption(s["rationale"])

            with col2:
                st.write("")
                st.write("Was this a helpful swap?")

                sub_id = s["sub_id"]
                current_vote = st.session_state.my_votes.get(sub_id)  # "up" / "down" / None

                # Button labels reflect your current vote so it's obvious
                # what clicking again will do (undo it).
                up_label = "✅ Upvoted (tap to undo)" if current_vote == "up" else "👍 Upvote"
                down_label = "✅ Downvoted (tap to undo)" if current_vote == "down" else "👎 Downvote"

                up_col, down_col = st.columns(2)
                if up_col.button(up_label, key=f"up_{sub_id}"):
                    if current_vote == "up":
                        # Undo an existing upvote.
                        database.adjust_vote(sub_id, upvote_delta=-1)
                        st.session_state.my_votes[sub_id] = None
                    elif current_vote == "down":
                        # Switch a downvote to an upvote.
                        database.adjust_vote(sub_id, upvote_delta=1, downvote_delta=-1)
                        st.session_state.my_votes[sub_id] = "up"
                    else:
                        # Cast a brand new upvote.
                        database.adjust_vote(sub_id, upvote_delta=1)
                        st.session_state.my_votes[sub_id] = "up"
                    st.rerun()

                if down_col.button(down_label, key=f"down_{sub_id}"):
                    if current_vote == "down":
                        # Undo an existing downvote.
                        database.adjust_vote(sub_id, downvote_delta=-1)
                        st.session_state.my_votes[sub_id] = None
                    elif current_vote == "up":
                        # Switch an upvote to a downvote.
                        database.adjust_vote(sub_id, upvote_delta=-1, downvote_delta=1)
                        st.session_state.my_votes[sub_id] = "down"
                    else:
                        # Cast a brand new downvote.
                        database.adjust_vote(sub_id, downvote_delta=1)
                        st.session_state.my_votes[sub_id] = "down"
                    st.rerun()

                up_count, down_count = database.get_vote_counts(sub_id)
                st.caption(f"{up_count} upvotes · {down_count} downvotes from the community")

            st.divider()

st.caption(
    "Nutrition values are per 100g/100ml, curated in the style of USDA FoodData "
    "Central for demonstration purposes. See README.md for data sources and how "
    "certainty scores are calculated."
)
