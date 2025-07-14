"""Houses code related to scoring evidence."""

FRAMEWORK = [
    {
        "step": "Step 1A: Allele or Haplotype",
        "categories": [
            {
                "category": "Allele",
                "points": 0,
            },
            {
                "category": "Haplotype",
                "points": 2,
            },
        ],
    },
    {
        "step": "Step 1B: Allele Resolution",
        "categories": [
            {
                "category": "1-field (see Step 6B)",
                "points": 0,
            },
            {
                "category": "2-field",
                "points": 1,
            },
            {
                "category": "3-field, G-group, P-group",
                "points": 2,
            },
            {
                "category": "4-field",
                "points": 3,
            },
        ],
    },
]
