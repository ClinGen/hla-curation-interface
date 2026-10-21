"""Houses constants used in the curation app's scoring_summary module.

Most of these come from the taskforce's scoring summary spreadsheet. The scoring
matrix (`FRAMEWORK` in `views.py`) has no equivalent for them.
"""


class SummaryKind:
    """Defines how a scoring summary category treats its rows."""

    # Counts the studies in each row but awards no points.
    DESIGN = "design"
    POINTS = "points"
    MULTIPLIER = "multiplier"


STUDY_DESIGN_CATEGORY = "Study design"
STUDY_DESIGN_STEP = "Sets thresholds used in 3A and 4"

# The spreadsheet's evidence categories and their kinds, keyed by the start of
# their steps' score attribute names.
EVIDENCE_CATEGORIES = {
    "score_step_1": ("Allele / haplotype", SummaryKind.POINTS),
    "score_step_2": ("Typing method", SummaryKind.POINTS),
    "score_step_3": ("Statistical evidence", SummaryKind.POINTS),
    "score_step_4": ("Cohort", SummaryKind.POINTS),
    "score_step_5": ("Phenotype", SummaryKind.POINTS),
    "score_step_6": ("Multipliers", SummaryKind.MULTIPLIER),
}

# Step 3C awards both of its categories, so the evidence scoring summary gives
# each its own column, named after the scoring matrix's footnote.
EVIDENCE_COLUMN_CATEGORIES = {
    "score_step_3c1": "OR/RR/Beta",
    "score_step_3c2": "CI",
}

MULTIPLIER_NOTE = "Applied per publication"
