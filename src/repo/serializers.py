"""Serializers for the repo app."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from curation.models import Evidence
    from repo.models import PublishedCuration


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
                    {"name": a.name, "slug": a.slug}
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
            "classification": curation.classification,
            "score": float(curation.score),
            **entity_data,
            "disease": (
                {
                    "name": curation.disease.name,
                    "mondo_id": curation.disease.mondo_id,
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
        "is_conflicting": evidence.is_conflicting,
        "is_included": evidence.is_included,
        "publication": (
            {
                "slug": evidence.publication.slug,
                "title": evidence.publication.title,
                "author": evidence.publication.author,
                "pubmed_id": evidence.publication.pubmed_id,
                "doi": evidence.publication.doi,
            }
            if evidence.publication
            else None
        ),
        "is_gwas": evidence.is_gwas,
        "zygosity": evidence.zygosity,
        "phase_confirmed": evidence.phase_confirmed,
        "typing_method": evidence.typing_method,
        "demographics": [demo.group for demo in evidence.demographics.all()],
        "p_value": str(evidence.p_value) if evidence.p_value else None,
        "multiple_testing_correction": evidence.multiple_testing_correction,
        "effect_size_statistic": evidence.effect_size_statistic,
        "odds_ratio": str(evidence.odds_ratio) if evidence.odds_ratio else None,
        "relative_risk": (
            str(evidence.relative_risk) if evidence.relative_risk else None
        ),
        "beta": str(evidence.beta) if evidence.beta else None,
        "ci_start": str(evidence.ci_start) if evidence.ci_start else None,
        "ci_end": str(evidence.ci_end) if evidence.ci_end else None,
        "cohort_size": evidence.cohort_size,
        "additional_phenotypes": evidence.additional_phenotypes,
        "has_association": evidence.has_association,
        "is_protective": evidence.is_protective,
        "needs_review": evidence.needs_review,
        "score": float(evidence.score),
        "added_at": evidence.added_at.isoformat(),
    }
