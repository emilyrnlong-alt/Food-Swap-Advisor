# 🥗 Food Swap Advisor

A Streamlit-run python app that takes a food you eat and suggests healthier alternatives by comparing USFD (United States Food Data) nutritional data like calories, fiber, sugar, protein, sodium, and carbs with a **% certainty score** that adapts over time as users upvote or downvote each suggestion.

```
"Potato chips" → 85% certainty → "Air-popped popcorn"  (+more fiber, -sodium, -calories)
```

## Why this project

As someone interested in health and nutrition as a means to better my habits, most nutrition apps I have used utilise solely objective data that does not take into consideration the more personal aspects of finding healthier food options like taste, texture and general acceptance of a substitution. This one makes a *recommendation* and is transparent about how confident it is in that recommendation, while taking into consideration more personal preferences like sensory and eating experience. Over time, as more users utilize the upvotes and shaped by community feedback.

## Features

- **Search or browse** a 109-food nutrition database (109 items covering ~55 common foods and their curated healthier substitutes, some substitutes reused across multiple originals — e.g. "grilled chicken breast" replaces both fried chicken and chicken nuggets).
- **Side-by-side nutrition-facts-style cards** with per-nutrient color coding (green = improvement, red = worse) vs. the original food.
- **Certainty score (0–100%)** per substitution, computed with a Bayesian average (see [How certainty is calculated](#how-certainty-is-calculated)).
- **Upvote / downvote** buttons that immediately shift the certainty score for users that see that swap next.
- Clean, custom-styled UI (nutrition-label-inspired theme) built in Streamlit (no separate frontend framework needed.)

## Project structure

```
food-swap-advisor/
├── app.py                  # Streamlit UI — the entry point
├── database.py             # SQLite schema + all data access functions
├── voting.py                # Certainty scoring math (Bayesian blend)
├── seed_database.py        # Loads data/*.csv into foodswap.db
├── generate_data.py         # Source-of-truth script that produced the CSVs
├── data/
│   ├── foods.csv            # 109 foods, nutrition per 100g/100ml
│   └── substitutions.csv    # original → substitute links + rationale
├── requirements.txt
└── README.md
```

## Setup

```bash
git clone <Food-Swap_Advisor>
cd food-swap-advisor
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python seed_database.py           # creates & populates foodswap.db
streamlit run app.py
```

**LOCAL ACCESS**: (https://food-swap-advisor-ewtuw2ojedhzvk386gwvpw.streamlit.app).

To reset your data (wipes votes and reloads from the CSVs):

```bash
python seed_database.py --force
```

## How certainty is calculated

Each substitution starts with a **curated `base_certainty`** (0–100), set based the degree to which the swap is better nutritionally (e.g. swapping soda for sparkling water removes 100% of the added sugar → 95% base certainty; swapping regular beer for light beer is a smaller win → 58%).

To ensure both upvotes and downvotes are weighed equally, the curated score is treated as a **prior worth 10 pseudo-votes** and blended with real votes, also known as the same idea behind IMDB's weighted movie ratings:

```python
PRIOR_WEIGHT = 10
prior_upvotes   = PRIOR_WEIGHT * (base_certainty / 100)
prior_downvotes = PRIOR_WEIGHT * (1 - base_certainty / 100)

certainty = (prior_upvotes + upvotes) / (PRIOR_WEIGHT + upvotes + downvotes) * 100
```

With 0 real votes, certainty == base_certainty exactly. As real votes accumulate, the score smoothly slides toward the community's actual opinion. See `voting.py` for the implementation and `voting.certainty_label()` for the "High / Moderate / Low confidence" badge thresholds.

## Data source & accuracy note

Nutrition values are curated, representative figures written in the style of the [USDA FoodData Central](https://fdc.nal.usda.gov/) database (per 100g/100ml), intended for demonstration and learning purposes — **not** verified clinical or lab data. `generate_data.py` is the single source of truth for the dataset; edit the `FOODS` / `SUBS` lists there and rerun it to regenerate the CSVs.

### Swapping in the real USDA API

To pull live, authoritative nutrition data instead of the curated CSVs:

1. Get a free API key at https://fdc.nal.usda.gov/api-key-signup.
2. Use the `/foods/search` and `/food/{fdcId}` endpoints to fetch a food's `Nutrient` list (calories = `Energy`, fiber = `Fiber, total dietary`, etc.).
3. Replace the body of `database.get_food_by_name` with an API call (add simple in-memory or SQLite caching so you're not hitting the API on every keystroke — same idea as `app.py`'s `@st.cache_data` on `cached_food_names`).

## Design decisions worth mentioning in an interview

- **SQLite over CSV-only or in-memory dicts**: models the original food ↔ substitute relationship as a real many-to-many edge table (`substitutions`), which made "reuse this substitute for multiple originals" trivial and kept vote counts durable across app restarts.
- **Bayesian-average certainty score** instead of a raw vote ratio, to avoid small-sample overconfidence — a real statistics concept (shrinkage estimation) applied to a practical UI problem.
- **Separation of concerns**: `database.py` never touches Streamlit, `voting.py` never touches SQL — each module is independently unit-testable.
- **`st.cache_data`** on the rarely-changing food name list, while deliberately *not* caching vote counts, to balance performance against correctness.

## Potential extensions

- Swap the curated CSVs for the live USDA FDC API.
- Add user accounts so one person can't upvote the same swap excessively (currently votes are anonymous/unlimited).
- A `st.bar_chart` comparing the nutrient deltas visually instead of just the text-based facts card.
