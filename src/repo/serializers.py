from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from repo.constants import PUBLIC_CURATION_FIELDS, PUBLIC_EVIDENCE_FIELDS

if TYPE_CHECKING:
    from curation.models import Curation, Evidence
    from repo.models import PublishedCuration

# Export keys that differ from the model field name, kept for existing consumers.
EXPORT_NAMES = {"taskforce_classification": "classification"}

# Public curation fields that the flat row lists after its fixed leading columns.
# The classification comes first, with the other identifying columns.
_ROW_TRAILING_FIELDS = sorted(PUBLIC_CURATION_FIELDS - {"taskforce_classification"})


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


def _flat_value(value: object) -> object:
    """Converts a model field value to a flat-file value.

    Returns:
        An empty string for None, otherwise the JSON-friendly value.
    """
    return "" if value is None else _export_value(value)


def flatten_published_curation(
    published: "PublishedCuration", url: str
) -> dict[str, object]:
    """Flattens a published curation to one row for a CSV or spreadsheet.

    A haplotype is represented by its name alone, since the name already lists
    its alleles. Evidence isn't included; the JSON export has it.

    Args:
        published: The PublishedCuration instance to flatten.
        url: The absolute URL of the curation's HLArepo page.

    Returns:
        An ordered mapping of column name to value, with None as an empty string.
    """
    curation = published.curation
    allele = curation.allele
    haplotype = curation.haplotype
    disease = curation.disease
    row: dict[str, object] = {
        "curation_id": curation.slug,
        "url": url,
        "version": published.version,
        "published_at": published.published_at.isoformat(),
        "allele": allele.name if allele else "",
        "allele_car_id": _flat_value(allele.car_id) if allele else "",
        "haplotype": haplotype.name if haplotype else "",
        "disease": disease.name if disease else "",
        "disease_mondo_id": _flat_value(disease.mondo_id) if disease else "",
        "disease_iri": _flat_value(disease.iri) if disease else "",
        EXPORT_NAMES["taskforce_classification"]: curation.classification_display,
        "score": _flat_value(curation.score),
    }
    for name in _ROW_TRAILING_FIELDS:
        row[EXPORT_NAMES.get(name, name)] = _flat_value(getattr(curation, name))
    row["copied_from"] = curation.copied_from.slug if curation.copied_from else ""
    return row
