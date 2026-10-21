"""Builds the scoring summary table for a curation.

The table follows the taskforce's spreadsheet, with the scoring matrix's labels.
For each category in the scoring framework, it counts the included evidence that
landed there, totals the points before multipliers, and totals the points that
count toward the score after each publication's multipliers.
"""

from dataclasses import dataclass, field
from typing import Any, cast

from curation.constants.models.curation import CURATION_TYPE_CHOICES, CurationTypes
from curation.constants.scoring_summary import (
    EVIDENCE_CATEGORIES,
    EVIDENCE_COLUMN_CATEGORIES,
    MULTIPLIER_NOTE,
    STUDY_DESIGN_CATEGORY,
    STUDY_DESIGN_STEP,
    SummaryKind,
)
from curation.constants.views import FRAMEWORK, GWAS_LABELS
from curation.interval import Interval
from curation.models import Curation, Evidence
from repo.serializers import format_decimal


@dataclass(frozen=True)
class _RowSpec:
    """A category in the framework, matched when the evidence's attr equals value."""

    label: str
    attr: str
    value: Any  # ruff: ignore[any-type] (Points are floats; GWAS is a boolean.)


@dataclass(frozen=True)
class _StepSpec:
    label: str
    rows: tuple[_RowSpec, ...]
    max_points: float | None = None


@dataclass(frozen=True)
class _CategorySpec:
    name: str
    steps: tuple[_StepSpec, ...]
    kind: str = SummaryKind.POINTS


_GWAS_LABEL, _NON_GWAS_LABEL = GWAS_LABELS

_STUDY_DESIGN = _CategorySpec(
    STUDY_DESIGN_CATEGORY,
    (
        _StepSpec(
            STUDY_DESIGN_STEP,
            (
                _RowSpec(_GWAS_LABEL, "is_gwas", value=True),
                _RowSpec(_NON_GWAS_LABEL, "is_gwas", value=False),
            ),
        ),
    ),
    kind=SummaryKind.DESIGN,
)


def _threshold(interval: Interval) -> str:
    """Returns an interval as the threshold a person would write, e.g., "<5E-8".

    A bracket with both ends inclusive shows its range, joined by an en dash. A
    bracket with an open upper end shows only that end, since the rows above and
    below it already give its lower end.

    Returns:
        The threshold, with numbers formatted as elsewhere in the interface.
    """
    start = format_decimal(interval.start)
    end = format_decimal(interval.end)
    if interval.end.is_infinite():
        return f"{'≥' if interval.start_inclusive else '>'}{start}"
    if interval.start.is_infinite() or not interval.start_inclusive:
        return f"{'≤' if interval.end_inclusive else '<'}{end}"
    if interval.end_inclusive:
        return f"{start}\N{EN DASH}{end}"
    return f"<{end}"


def _category_label(row: dict[str, Any]) -> str:
    """Returns a framework row's category as text, with thresholds for intervals.

    Returns:
        The category, e.g., "<5E-8 / <0.01" for a GWAS and non-GWAS bracket, or
        "OR/RR ≥2 or ≤0.5; Beta ≥0.5 or ≤-0.5" for effect sizes.
    """
    category = row["category"]
    if isinstance(category, str):
        return category.strip()
    if row["split_horizontal"]:
        return " / ".join(_threshold(interval) for interval in category)
    by_variable: dict[str, list[str]] = {}
    for interval in category:
        by_variable.setdefault(interval.variable, []).append(_threshold(interval))
    return "; ".join(
        f"{variable} {' or '.join(thresholds)}"
        for variable, thresholds in by_variable.items()
    )


def _max_points(rows: list[_RowSpec]) -> float:
    """Returns a step's maximum: the best category of each of its score attributes.

    Step 3C awards both of its categories' points, so its maximum is their sum.

    Returns:
        The maximum points for the step.
    """
    best: dict[str, float] = {}
    for row in rows:
        best[row.attr] = max(best.get(row.attr, row.value), row.value)
    return sum(best.values())


def _framework() -> tuple[_CategorySpec, ...]:
    """Returns the table's categories, built from the scoring matrix's framework.

    The labels are the scoring matrix's, so the two stay in step. The matrix's
    GWAS and non-GWAS heading rows and its totals award no points, so the summary
    leaves them out.

    Returns:
        The study design category, then the framework's steps by evidence category.
    """
    steps: list[tuple[str, list[_RowSpec]]] = []
    # The framework mixes value types per key, so read its rows loosely.
    for row in cast("list[dict[str, Any]]", FRAMEWORK):
        if row.get("is_total_row"):
            continue
        # Steps 3A and 4 name the step on their GWAS and non-GWAS heading row.
        if row["text"]:
            steps.append((row["text"], []))
        if row["points"] == "":
            continue
        steps[-1][1].append(_RowSpec(_category_label(row), row["score"], row["points"]))
    categories: dict[tuple[str, str], list[_StepSpec]] = {}
    for label, rows in steps:
        name, kind = EVIDENCE_CATEGORIES[rows[0].attr[: len("score_step_1")]]
        is_multiplier = kind == SummaryKind.MULTIPLIER
        categories.setdefault((name, kind), []).append(
            _StepSpec(label, tuple(rows), None if is_multiplier else _max_points(rows))
        )
    return (
        _STUDY_DESIGN,
        *(
            _CategorySpec(name, tuple(category_steps), kind)
            for (name, kind), category_steps in categories.items()
        ),
    )


_FRAMEWORK = _framework()


@dataclass
class SummaryRow:
    label: str
    points: Any  # ruff: ignore[any-type] (None for study design rows.)
    count: int


@dataclass
class SummaryStep:
    label: str
    rows: list[SummaryRow]
    max_points: float | None
    total: float | None


@dataclass
class SummaryCategory:
    name: str
    kind: str
    steps: list[SummaryStep]
    counted: float | None = None
    note: str = ""
    num_rows: int = field(init=False)

    def __post_init__(self) -> None:
        self.num_rows = sum(len(step.rows) for step in self.steps)

    @property
    def is_design(self) -> bool:
        return self.kind == SummaryKind.DESIGN

    @property
    def is_points(self) -> bool:
        return self.kind == SummaryKind.POINTS

    @property
    def is_multiplier(self) -> bool:
        return self.kind == SummaryKind.MULTIPLIER


@dataclass
class _Pair:
    """The HLA-disease pair a summary's header names."""

    subject_type: str
    subject: str
    car_id: str
    disease: str
    mondo_id: str


@dataclass
class ScoringSummary(_Pair):
    num_publications: int
    categories: list[SummaryCategory]
    total_score: float


def build_scoring_summary(curation: Curation) -> ScoringSummary:
    """Returns the scoring summary for the curation's included evidence.

    Args:
        curation: The curation to summarize.

    Returns:
        The table's header values, rows, and totals.
    """
    evidence = _included_evidence(curation)
    categories = [_category(spec, evidence) for spec in _FRAMEWORK]
    return ScoringSummary(
        **_pair(curation),
        # A publication can have more than one evidence item.
        num_publications=len({e.publication.pk for e in evidence if e.publication}),
        categories=categories,
        total_score=sum(c.counted for c in categories if c.counted is not None),
    )


def _evidence_columns() -> tuple[tuple[str, str], ...]:
    """Returns the evidence scoring summary's step columns, in the framework's order.

    Each column is named after its score attribute, e.g., "1A" for score_step_1a.
    Step 3C's two attributes are named after their categories, e.g., "3C: CI".

    Returns:
        Each column's label and score attribute.
    """
    rows = cast("list[dict[str, Any]]", FRAMEWORK)
    attrs = dict.fromkeys(
        row["score"] for row in rows if row["score"].startswith("score_step_")
    )
    columns = []
    for attr in attrs:
        step = attr.removeprefix("score_step_").upper()
        if category := EVIDENCE_COLUMN_CATEGORIES.get(attr):
            step = f"{step.rstrip('0123456789')}: {category}"
        columns.append((step, attr))
    return tuple(columns)


_EVIDENCE_COLUMNS = _evidence_columns()


@dataclass
class EvidenceScoreRow:
    pmid: str
    points: list[float | None]
    total: float


@dataclass
class EvidenceScoringSummary(_Pair):
    columns: list[str]
    rows: list[EvidenceScoreRow]


def build_evidence_scoring_summary(curation: Curation) -> EvidenceScoringSummary:
    """Returns each included evidence item's points for each scoring step.

    Args:
        curation: The curation to summarize.

    Returns:
        The table's header values, step columns, and one row per evidence item.
    """
    return EvidenceScoringSummary(
        **_pair(curation),
        columns=[label for label, _ in _EVIDENCE_COLUMNS],
        rows=[
            EvidenceScoreRow(
                pmid=e.publication.pubmed_id if e.publication else e.slug,
                points=[getattr(e, attr) for _, attr in _EVIDENCE_COLUMNS],
                total=e.score,
            )
            for e in _included_evidence(curation)
        ],
    )


def _pair(curation: Curation) -> dict[str, str]:
    """Returns the header fields that name the curation's HLA-disease pair."""
    is_haplotype = curation.curation_type == CurationTypes.HAPLOTYPE
    subject = curation.haplotype if is_haplotype else curation.allele
    # Haplotypes have no CAR ID of their own.
    car_id = "" if is_haplotype or not curation.allele else curation.allele.car_id
    return {
        "subject_type": CURATION_TYPE_CHOICES[curation.curation_type],
        "subject": subject.display_name if subject else "",
        "car_id": car_id or "",
        "disease": curation.disease.name,
        "mondo_id": curation.disease.mondo_id or "",
    }


def _included_evidence(curation: Curation) -> list[Evidence]:
    return list(
        curation.evidence.filter(is_included=True)  # type: ignore
        .select_related("curation", "publication")
        .order_by("pk")
    )


def _category(spec: _CategorySpec, evidence: list[Evidence]) -> SummaryCategory:
    steps = [
        SummaryStep(
            label=step.label,
            rows=[
                SummaryRow(
                    label=row.label,
                    points=None if spec.kind == SummaryKind.DESIGN else row.value,
                    count=sum(getattr(e, row.attr) == row.value for e in evidence),
                )
                for row in step.rows
            ],
            max_points=step.max_points,
            total=_sum_points(evidence, _attrs(step))
            if spec.kind == SummaryKind.POINTS
            else None,
        )
        for step in spec.steps
    ]
    category = SummaryCategory(name=spec.name, kind=spec.kind, steps=steps)
    if spec.kind == SummaryKind.POINTS:
        attrs = [attr for step in spec.steps for attr in _attrs(step)]
        category.counted = sum(
            _sum_points([e], attrs) * e.score_step_6a * e.score_step_6b
            for e in evidence
        )
    elif spec.kind == SummaryKind.MULTIPLIER:
        category.note = _multiplier_note(evidence)
    return category


def _attrs(step: _StepSpec) -> list[str]:
    """Returns the step's score attributes, once each, in order."""
    return list(dict.fromkeys(row.attr for row in step.rows))


def _sum_points(evidence: list[Evidence], attrs: list[str]) -> float:
    return sum(
        points
        for e in evidence
        for attr in attrs
        if (points := getattr(e, attr)) is not None
    )


def _multiplier_note(evidence: list[Evidence]) -> str:
    """Returns which multiplier each publication got.

    Most publications get a multiplier of 1, so those are counted; the others list
    their PMIDs.

    Returns:
        The note, starting with MULTIPLIER_NOTE.
    """
    by_multiplier: dict[float, list[Evidence]] = {}
    for e in evidence:
        by_multiplier.setdefault(e.score_step_6a * e.score_step_6b, []).append(e)
    parts = [MULTIPLIER_NOTE]
    for multiplier in sorted(by_multiplier, reverse=True):
        group = by_multiplier[multiplier]
        if multiplier == 1:
            noun = "study" if len(group) == 1 else "studies"
            parts.append(f"\N{MULTIPLICATION SIGN}1 in {len(group)} {noun}")
        else:
            ids = ", ".join(
                dict.fromkeys(
                    e.publication.pubmed_id if e.publication else e.slug for e in group
                )
            )
            parts.append(f"\N{MULTIPLICATION SIGN}{multiplier:g} in PMID: {ids}")
    return "; ".join(parts)
