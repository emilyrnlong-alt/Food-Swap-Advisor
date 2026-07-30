"""
voting.py
---------
Turns (base_certainty, upvotes, downvotes) into a single 0-100 "% certainty
this is a healthier option" score shown in the UI.

Why not just `upvotes / (upvotes + downvotes)`?
Because with 0 or 1 votes that ratio is either undefined or wildly
overconfident (1 upvote -> 100%). Instead we use a Bayesian average: the
curator's `base_certainty` acts as a prior worth PRIOR_WEIGHT "pseudo
votes", so a brand-new substitution starts at exactly the curated value
and gradually shifts toward the community's real vote ratio as more
votes come in. This is the same smoothing idea used by IMDB's weighted
movie ratings and by Reddit/Wilson-score style ranking.

    prior_upvotes   = PRIOR_WEIGHT * (base_certainty / 100)
    prior_downvotes = PRIOR_WEIGHT * (1 - base_certainty / 100)

    certainty = (prior_upvotes + upvotes)
                / (PRIOR_WEIGHT + upvotes + downvotes)
                * 100

PRIOR_WEIGHT controls how quickly community votes can move the needle:
lower = votes matter more / faster; higher = curated score is "stickier".
"""

PRIOR_WEIGHT = 10.0  # equivalent to 10 curated pseudo-votes


def compute_certainty(base_certainty: float, upvotes: int, downvotes: int) -> float:
    prior_upvotes = PRIOR_WEIGHT * (base_certainty / 100.0)
    prior_downvotes = PRIOR_WEIGHT * (1.0 - base_certainty / 100.0)

    total_weight = PRIOR_WEIGHT + upvotes + downvotes
    certainty = (prior_upvotes + upvotes) / total_weight * 100.0
    return round(certainty, 1)


def certainty_label(certainty: float) -> str:
    """Human-readable confidence bucket, used for badge coloring in the UI."""
    if certainty >= 75:
        return "High confidence"
    if certainty >= 50:
        return "Moderate confidence"
    return "Low confidence"
