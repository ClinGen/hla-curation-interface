from datetime import UTC, date
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from repo.constants import PUBLIC_CURATION_FIELDS, PUBLIC_EVIDENCE_FIELDS

if TYPE_CHECKING:
    from django.db.models import Model

    from curation.models import Curation, Evidence
    from repo.models import PublishedCuration

# Export keys that differ from the model field name, kept for existing consumers.
EXPORT_NAMES = {"taskforce_classification": "classification"}


def _export_value(value: object) -> object:
    """Converts a model field value to a JSON-friendly value.

    Returns:
        Dates as ISO strings, decimals as strings, and anything else unchanged.
    """
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value


def _public_curation_fields(curation: "Curation") -> dict[str, Any]:
    return {
        EXPORT_NAMES.get(name, name): _export_value(getattr(curation, name))
        for name in sorted(PUBLIC_CURATION_FIELDS)
    }


def _public_evidence_fields(evidence: "Evidence") -> dict[str, Any]:
    data: dict[str, Any] = {}
    for name in sorted(PUBLIC_EVIDENCE_FIELDS):
        if name == "demographics":
            data[name] = [demo.group for demo in evidence.demographics.all()]
        else:
            data[name] = _export_value(getattr(evidence, name))
    return data


def serialize_published_curation(published: "PublishedCuration") -> dict[str, Any]:
    """Serializes a published curation to a dictionary.

    Args:
        published: The PublishedCuration instance to serialize.

    Returns:
        Dictionary with all curation data including related evidence.
    """
    curation = published.curation

    # Determine entity (allele or haplotype).
    entity_data = {}
    if curation.curation_type == "ALL" and curation.allele:
        entity_data = {
            "type": "allele",
            "allele": {
                "name": curation.allele.name,
                "slug": curation.allele.slug,
                "car_id": curation.allele.car_id,
            },
        }
    elif curation.curation_type == "HAP" and curation.haplotype:
        entity_data = {
            "type": "haplotype",
            "haplotype": {
                "name": curation.haplotype.name,
                "slug": curation.haplotype.slug,
                "alleles": [
                    {"name": a.name, "slug": a.slug, "car_id": a.car_id}
                    for a in curation.haplotype.alleles.all()
                ],
            },
        }

    return {
        "curation_id": curation.slug,
        "published_at": published.published_at.isoformat(),
        "published_by": (
            published.published_by.username if published.published_by else None
        ),
        "version": published.version,
        "curation": {
            "status": curation.status,
            **_public_curation_fields(curation),
            "copied_from": curation.copied_from.slug if curation.copied_from else None,
            "score": float(curation.score),
            **entity_data,
            "disease": (
                {
                    "name": curation.disease.name,
                    "mondo_id": curation.disease.mondo_id,
                    "iri": curation.disease.iri,
                    "slug": curation.disease.slug,
                }
                if curation.disease
                else None
            ),
            "added_at": curation.added_at.isoformat(),
        },
        "evidence": [
            serialize_evidence(evidence) for evidence in curation.evidence.all()
        ],
    }


def serialize_evidence(evidence: "Evidence") -> dict[str, Any]:
    """Serializes an evidence record to a dictionary.

    Args:
        evidence: The Evidence instance to serialize.

    Returns:
        Dictionary with all evidence data.
    """
    return {
        "evidence_id": evidence.slug,
        "status": evidence.status,
        "is_included": evidence.is_included,
        "publication": (
            {
                "slug": evidence.publication.slug,
                "title": evidence.publication.title,
                "author": evidence.publication.author,
                "pubmed_id": evidence.publication.pubmed_id,
            }
            if evidence.publication
            else None
        ),
        **_public_evidence_fields(evidence),
        "score": float(evidence.score),
        "added_at": evidence.added_at.isoformat(),
    }


# Readable column names for the public fields in a flat row, in the order the
# forms ask for them. The classification itself has a fixed column.
CLASSIFICATION_COLUMNS = {
    "taskforce": "Taskforce",
    "taskforce_review_date": "Taskforce Review Date",
    "taskforce_evidence_summary": "Taskforce Evidence Summary",
    "taskforce_override_reason": "Taskforce Override Reason",
    "taskforce_additional_notes": "Taskforce Additional Notes",
}
EVIDENCE_COLUMNS = {
    "is_gwas": "GWAS",
    "zygosity": "Zygosity",
    "phase_confirmed": "Phase Confirmed",
    "typing_method": "Typing Method",
    "demographics": "Demographics",
    "p_value": "p-value",
    "multiple_testing_correction": "Multiple Testing Correction",
    "effect_size_statistic": "Effect Size Statistic",
    "odds_ratio": "Odds Ratio",
    "relative_risk": "Relative Risk",
    "beta": "Beta Coefficient",
    "ci_start": "Confidence Interval Start",
    "ci_end": "Confidence Interval End",
    "cohort_size": "Cohort Size",
    "additional_phenotypes": "Additional Phenotypes",
    "has_association": "Has Association",
    "is_protective": "Protective",
}

# The evidence columns of a flat row, in order, so a classification without
# evidence can still fill them in with blanks.
EVIDENCE_COLUMN_NAMES = [
    "Evidence ID",
    "Included in Score",
    "Evidence Score",
    "Publication ID",
    "Publication Title",
    "Publication Author",
    "PubMed ID",
    *EVIDENCE_COLUMNS.values(),
]


def _flat_value(value: object) -> object:
    """Converts a model field value to a readable flat-file value.

    Returns:
        An empty string for None, Yes or No for a boolean, an ISO string for a
        date, and anything else unchanged. Decimals stay numbers so spreadsheets
        can sort and compute on them.
    """
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, date):
        return value.isoformat()
    return value


def _field_label(instance: "Model", name: str) -> object:
    """Returns a field's readable value, using the display label for a choice.

    Returns:
        The choice label for a field with choices, otherwise the flat value.
    """
    value = getattr(instance, name)
    # Django adds a get_<name>_display method for every field with choices.
    get_display = getattr(instance, f"get_{name}_display", None)
    if get_display is not None and value is not None:
        return get_display()
    return _flat_value(value)


def flatten_published_curation(
    published: "PublishedCuration", url: str
) -> dict[str, object]:
    """Flattens a published curation to its classification columns.

    A haplotype is represented by its name alone, since the name already lists
    its alleles.

    Args:
        published: The PublishedCuration instance to flatten.
        url: The absolute URL of the classification's HLArepo page.

    Returns:
        An ordered mapping of readable column name to readable value.
    """
    curation = published.curation
    allele = curation.allele
    haplotype = curation.haplotype
    disease = curation.disease
    published_at = published.published_at.astimezone(UTC)
    row: dict[str, object] = {
        "Curation ID": curation.slug,
        "URL": url,
        "Version": published.version,
        "Published (UTC)": published_at.strftime("%Y-%m-%d %H:%M"),
        "Allele": allele.name if allele else "",
        "Allele CAR ID": _flat_value(allele.car_id) if allele else "",
        "Haplotype": haplotype.name if haplotype else "",
        "Disease": disease.name if disease else "",
        "Disease MONDO ID": _flat_value(disease.mondo_id) if disease else "",
        "Disease IRI": _flat_value(disease.iri) if disease else "",
        "Classification": curation.classification_display,
        "Score": curation.score,
    }
    for name, column in CLASSIFICATION_COLUMNS.items():
        value = getattr(curation, name)
        if name == "taskforce":
            value = curation.taskforce_display
        row[column] = _flat_value(value)
    row["Update Of"] = curation.copied_from.slug if curation.copied_from else ""
    return row


def flatten_evidence(evidence: "Evidence") -> dict[str, object]:
    """Flattens an evidence record to its evidence columns.

    The publication is split into separate columns, and the demographic groups
    are joined with semicolons.

    Args:
        evidence: The Evidence instance to flatten.

    Returns:
        An ordered mapping of readable column name to readable value.
    """
    publication = evidence.publication
    row: dict[str, object] = {
        "Evidence ID": evidence.slug,
        "Included in Score": _flat_value(evidence.is_included),
        "Evidence Score": evidence.score,
        "Publication ID": publication.slug if publication else "",
        "Publication Title": publication.title if publication else "",
        "Publication Author": publication.author if publication else "",
        "PubMed ID": _flat_value(publication.pubmed_id) if publication else "",
    }
    for name, column in EVIDENCE_COLUMNS.items():
        if name == "demographics":
            groups = evidence.demographics.all()
            row[column] = "; ".join(demo.group for demo in groups)
        else:
            row[column] = _field_label(evidence, name)
    return row


def flatten_classification_rows(
    published: "PublishedCuration", url: str
) -> list[dict[str, object]]:
    """Flattens a published curation to one row per evidence record.

    Each row has the classification columns followed by one evidence record's
    columns. A classification without evidence gets one row with blank evidence
    columns, so it still appears in the file.

    Args:
        published: The PublishedCuration instance to flatten.
        url: The absolute URL of the classification's HLArepo page.

    Returns:
        The rows, each an ordered mapping of readable column name to value.
    """
    classification = flatten_published_curation(published, url=url)
    evidence_rows = [
        flatten_evidence(evidence) for evidence in published.curation.evidence.all()
    ]
    if not evidence_rows:
        evidence_rows = [dict.fromkeys(EVIDENCE_COLUMN_NAMES, "")]
    return [{**classification, **evidence} for evidence in evidence_rows]
