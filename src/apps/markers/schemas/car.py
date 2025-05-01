"""Define schemas for the ClinGen Allele Registry API."""

from collections.abc import Iterator

from pydantic import BaseModel, Field, RootModel, field_validator

# ======================================================================================
# HLA Descriptor API Response Schema
# ----------------------------------
# The following classes represent the JSON response from the ClinGen Allele Registry
# API for the HLA descriptor endpoint: https://reg.genome.network/allele/hla/desc/.
#
# Example from 2025-04-29:
# [
#   {
#     "@id": "https://reg.clinicalgenome.org/allele/CAHLA1449130330",
#     "hlaFields": [
#       {
#         "alleleGroup": "01",
#         "descriptor": "A*01:01:01:119",
#         "gene": "A",
#         "hlaProtein": "01",
#         "nonCoding": "119",
#         "synonDnaSub": "01"
#       }
#     ],
#     "id": "CAHLA1449130330",
#     "type": "hla"
#   }
# ]
# ======================================================================================


class HLADescriptorField(BaseModel):
    """Represent the individual fields within an HLA descriptor.

    HLA allele names are represented as strings of the form:
        HLA-<descriptor>

    Where <descriptor> is a string of the form:
        <gene_name>*<allele_group>:<f1_allele_group>:<f2_hla_protein>:<f3_synon_dna_sub>:<f4_non_coding><suffix>

    Not all alleles have all fields. Not all alleles have a suffix. Generally, the
    'HLA-' portion of the name is omitted when referring to an allele.

    For more information, see:
        https://hla.alleles.org/pages/nomenclature/naming_alleles/
    """

    # fmt: off
    descriptor: str = Field(
        alias="descriptor",
        description="The whole descriptor for the allele, e.g., 'A*01:01:01:119'."
    )
    gene_name: str = Field(
        alias="gene",
        description="The HLA gene."
    )
    f1_allele_group: str = Field(
        alias="alleleGroup",
        description="The allele group."
    )
    f2_hla_protein: str = Field(
        alias="hlaProtein",
        description="The specific HLA protein."
    )
    f3_synon_dna_sub: str | None = Field(
        alias="synonDnaSub",
        description="Used to show a synonymous DNA substitution within the coding region."  # noqa: E501 (I'd like to preserve the structure of this block.)
    )
    f4_non_coding: str | None = Field(
        alias="nonCoding",
        description="Used to show differences in a non-coding region."
    )
    # fmt: on


class HLADescriptorRecord(BaseModel):
    """Represent a single HLA allele record from the API."""

    # fmt: off
    at_id: str = Field(
        alias="@id",
        description="The link to the same API response, but using the CAR ID."
    )
    hla_fields: list[HLADescriptorField] = Field(
        alias="hlaFields",
        description="The name of the HLA allele broken down into its components.",
    )
    car_id: str = Field(
        alias="id",
        description="The unique identifier for the HLA allele record in the CAR."
    )
    type: str = Field(
        alias="type",
        description="The type of the record, which is 'hla' for HLA alleles."
    )
    # fmt: on


class HLADescriptorSchema(RootModel):
    """Represents the top-level list of HLA allele records from the API."""

    root: list[HLADescriptorRecord]

    def __iter__(self) -> Iterator[HLADescriptorRecord]:  # type: ignore[override]
        """Return an iterator over the records in the schema."""
        return iter(self.root)

    def __getitem__(self, item: int) -> HLADescriptorRecord | None:
        """Return a record from the schema."""
        return self.root[item]

    @field_validator("root")
    def validate_list_length(
        cls,  # noqa: N805 (Pydantic conventions supersede lint conventions here.)
        v: list[HLADescriptorRecord],
    ) -> list[HLADescriptorRecord]:
        """Return the list of records, validating its length is 1.

        I'm not sure why the CAR decided to provide these endpoints where the top-level
        item is a list, but I want to make sure we're handling it correctly.

        Raises:
            ValueError: If the list of records is not of length 1.
        """
        if len(v) != 1:
            error_message = "List of records must be of length 1"
            raise ValueError(error_message)
        return v
