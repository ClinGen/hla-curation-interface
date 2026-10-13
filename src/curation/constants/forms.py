"""Houses constants used in the curation app's forms module."""

# Katrin Sangkuhl wrote this template for the taskforce's evidence summaries. Reviewers
# replace the bracketed text and drop the parts that don't apply.
EVIDENCE_SUMMARY_TEMPLATE = """\
[Allele/haplotype]\N{EN DASH}[Disease] Curation Summary

[Allele/haplotype] was first reported in association with [disease] by [Author] et al. \
[year] (PMID: [ ]). [If applicable: In case of haplotype, discuss structure]. \
[Disease] (MONDO:[ID]) is characterized by [one to three sentences on the core \
clinical phenotype, with citations]. [If applicable: Phenotypes in the included \
studies were mapped to MONDO:[ID]. However, [describe the problem, e.g., the studies \
used different diagnostic criteria or reported a broader/narrower phenotype or subtype \
than the MONDO term] (PMIDs: [ ]).] [Discuss if increased risk or protective \
association] [If applicable: Sentence if a specific disease phenotype contributed to \
the total score.]

The classification of the [allele/haplotype]\N{EN DASH}[disease] pair is based on \
evidence from [n] publications (PMIDs: [ ]). These were identified through a \
structured PubMed search and discussed within the ClinGen HLA Curation Taskforce \
(HCT). The evidence comprises [n] genome-wide association studies (GWAS) and [n] \
case-control studies. [The allele was heterozygous (monoallelic) in [n]/[N] of the \
scored evidence and homozygous in [n].] OR [The allele was heterozygous (monoallelic) \
in all studies.] All evidence was typed at 2-field resolution [, except for [n] \
studies where the genotyping method allowed 3-field [4-field] resolution]. [All / [n] \
of [N]] scored associations were statistically significant. [If applicable: In case, \
non-significant results are included, briefly discuss potential reasons for \
disagreement.] The total score for the [allele/haplotype]\N{EN DASH}[disease] pair is \
[x] points.

In summary, there is [classification] evidence supporting the association between \
[allele/haplotype] and [disease], based on the published HLA curation framework (PMID: \
[ ]; SOP version [x]). This classification was approved by the ClinGen HLA Curation \
Taskforce on [Final approval date]."""
