"""Lists the model fields that are public in HLArepo and the JSON export.

These sets are the one place that decides what's public. The serializers build
the export from them, and the forms mark these fields with a public badge.
Everything else, such as needs_review and every *_notes field on Evidence, stays
internal.
"""

PUBLIC_CURATION_FIELDS = frozenset(
    {
        "ep",
        "ep_additional_notes",
        "ep_classification",
        "ep_evidence_summary",
        "ep_override_reason",
        "ep_review_date",
    }
)

PUBLIC_EVIDENCE_FIELDS = frozenset(
    {
        "additional_phenotypes",
        "beta",
        "ci_end",
        "ci_start",
        "cohort_size",
        "demographics",
        "effect_size_statistic",
        "has_association",
        "is_gwas",
        "is_protective",
        "multiple_testing_correction",
        "odds_ratio",
        "p_value",
        "phase_confirmed",
        "relative_risk",
        "typing_method",
        "zygosity",
    }
)
