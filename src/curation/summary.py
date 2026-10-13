"""Builds the taskforce's evidence summary template for a curation.

Katrin Sangkuhl wrote the template. We fill in what the curation already knows and
leave the rest in brackets for the reviewer to replace or remove.
"""

from curation.constants.models.curation import (
    CLASSIFICATION_CHOICES,
    Classification,
    CurationTypes,
)
from curation.constants.models.evidence import Zygosity
from curation.models import Curation, Evidence

# Only these classifications read naturally as "there is [classification] evidence."
_EVIDENCE_LEVELS = (
    Classification.DEFINITIVE,
    Classification.STRONG,
    Classification.MODERATE,
    Classification.LIMITED,
)


def build_evidence_summary(curation: Curation) -> str:
    """Returns the evidence summary template with the curation's known values.

    Args:
        curation: The curation to summarize.

    Returns:
        The summary, with brackets around the parts the reviewer must write.
    """
    is_haplotype = curation.curation_type == CurationTypes.HAPLOTYPE
    subject = curation.haplotype if is_haplotype else curation.allele
    name = subject.display_name if subject else "[Allele/haplotype]"
    disease = curation.disease.name or "[disease]"
    pair = f"{name}\N{EN DASH}{disease}"
    evidence = list(
        curation.evidence.filter(is_included=True)  # type: ignore
        .select_related("publication")
        .order_by("pk")
    )
    return "\n\n".join(
        [
            f"{_capitalize(pair)} Curation Summary",
            _background(curation, name, disease, is_haplotype=is_haplotype),
            _evidence(curation, pair, evidence, is_haplotype=is_haplotype),
            _conclusion(curation, name, disease),
        ]
    )


def _background(
    curation: Curation, name: str, disease: str, *, is_haplotype: bool
) -> str:
    mondo_id = curation.disease.mondo_id or "MONDO:[ID]"
    sentences = []
    sentences.append(
        f"{name} was first reported in association with {disease} by [Author] et al. "
        "[year] (PMID: [ ]).",
    )
    if is_haplotype:
        sentences.append("[Discuss the haplotype structure.]")
    sentences.append(
        f"{_capitalize(disease)} ({mondo_id}) is characterized by [one to three "
        "sentences on the core clinical phenotype, with citations].",
    )
    sentences.append(
        "[If applicable: Phenotypes in the included studies were mapped to "
        f"{mondo_id}. However, [describe the problem, e.g., the studies used "
        "different diagnostic criteria or reported a broader/narrower phenotype or "
        "subtype than the MONDO term] (PMIDs: [ ]).]",
    )
    sentences.append("[Discuss if increased risk or protective association]")
    sentences.append(
        "[If applicable: Sentence if a specific disease phenotype contributed to "
        "the total score.]",
    )
    return " ".join(sentences)


def _evidence(
    curation: Curation, pair: str, evidence: list[Evidence], *, is_haplotype: bool
) -> str:
    if not evidence:
        return (
            f"The classification of the {pair} pair is based on evidence from [n] "
            "publications (PMIDs: [ ])."
        )
    publications = sorted(
        {e.publication for e in evidence if e.publication},
        key=lambda p: (p.publication_year or 0, p.pubmed_id),
    )
    one_publication = len(publications) == 1
    pmids = ", ".join(p.pubmed_id for p in publications)
    num_gwas = sum(e.is_gwas for e in evidence)
    study_types = [
        _count(
            num_gwas,
            "genome-wide association study (GWAS)",
            "genome-wide association studies (GWAS)",
        ),
        _count(len(evidence) - num_gwas, "case-control study", "case-control studies"),
    ]
    noun = "haplotype" if is_haplotype else "allele"
    sentences = []
    sentences.append(
        f"The classification of the {pair} pair is based on evidence from "
        f"{_count(len(publications), 'publication')} "
        f"({'PMID' if one_publication else 'PMIDs'}: {pmids}).",
    )
    sentences.append(
        f"{'This was' if one_publication else 'These were'} identified through a "
        "structured PubMed search and discussed within the ClinGen HLA Curation "
        "Taskforce (HCT).",
    )
    sentences.append(
        "The evidence comprises "
        f"{' and '.join(s for s in study_types if not s.startswith('0 '))}.",
    )
    sentences.append(_zygosity(evidence, noun))
    sentences.append(_resolution(evidence))
    sentences += _significance(evidence)
    sentences.append(
        f"The total score for the {pair} pair is {_count(curation.score, 'point')}."
    )
    return " ".join(sentences)


def _zygosity(evidence: list[Evidence], noun: str) -> str:
    num_biallelic = sum(e.zygosity == Zygosity.BIALLELIC for e in evidence)
    if not num_biallelic:
        return f"The {noun} was heterozygous (monoallelic) in all studies."
    num_monoallelic = len(evidence) - num_biallelic
    return (
        f"The {noun} was heterozygous (monoallelic) in "
        f"{num_monoallelic}/{len(evidence)} of the scored evidence and homozygous in "
        f"{num_biallelic}."
    )


def _resolution(evidence: list[Evidence]) -> str:
    fields = [e.num_fields for e in evidence]
    if None in fields:
        return (
            "All evidence was typed at 2-field resolution [, except for [n] studies "
            "where the genotyping method allowed 3-field [4-field] resolution]."
        )
    lowest = min(fields)
    sentence = f"All evidence was typed at {lowest}-field resolution"
    higher = [f for f in fields if f > lowest]
    if higher:
        allowed = " or ".join(f"{f}-field" for f in sorted(set(higher)))
        sentence += (
            f", except for {_count(len(higher), 'study', 'studies')} where the "
            f"genotyping method allowed {allowed} resolution"
        )
    return f"{sentence}."


def _significance(evidence: list[Evidence]) -> list[str]:
    num_significant = sum(e.has_association for e in evidence)
    if len(evidence) == 1:
        verb = "was" if num_significant else "was not"
        sentence = f"The scored association {verb} statistically significant."
    elif num_significant == len(evidence):
        sentence = "All scored associations were statistically significant."
    else:
        sentence = (
            f"{num_significant} of {len(evidence)} scored associations were "
            "statistically significant."
        )
    if num_significant < len(evidence):
        return [sentence, "[Briefly discuss potential reasons for disagreement.]"]
    return [sentence]


def _conclusion(curation: Curation, name: str, disease: str) -> str:
    code = curation.taskforce_classification or curation.suggested_classification
    if code in _EVIDENCE_LEVELS:
        classification = CLASSIFICATION_CHOICES[code].lower()
    else:
        classification = "[classification]"
    return (
        f"In summary, there is {classification} evidence supporting the association "
        f"between {name} and {disease}, based on the published HLA curation "
        "framework (PMID: [ ]; SOP version [x]). This classification was approved "
        "by the ClinGen HLA Curation Taskforce on [Final approval date]."
    )


def _count(n: float, singular: str, plural: str | None = None) -> str:
    """Returns the count with the singular or plural noun, e.g., "2 studies".

    Args:
        n: The count.
        singular: The noun for a count of one.
        plural: The noun for other counts. Defaults to the singular plus "s".

    Returns:
        The count and noun.
    """
    noun = singular if n == 1 else plural or f"{singular}s"
    return f"{n:g} {noun}"


def _capitalize(text: str) -> str:
    """Uppercases only the first character, unlike str.capitalize.

    Args:
        text: The text to capitalize.

    Returns:
        The text with its first character uppercased.
    """
    return text[:1].upper() + text[1:]
