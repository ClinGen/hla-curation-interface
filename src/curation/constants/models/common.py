"""Houses constants shared by multiple models."""


class CurationStatus:
    """Defines the workflow status codes for curations."""

    IN_PROGRESS = "INP"
    PROVISIONAL = "PRV"
    APPROVED = "APR"
    PUBLISHED = "PUB"


STATUS_CHOICES = {
    CurationStatus.IN_PROGRESS: "In Progress",
    CurationStatus.PROVISIONAL: "Provisional",
    CurationStatus.APPROVED: "Approved",
    CurationStatus.PUBLISHED: "Published",
}


class EvidenceStatus:
    """Defines the status codes for evidence."""

    IN_PROGRESS = "INP"
    DONE = "DNE"


EVIDENCE_STATUS_CHOICES = {
    EvidenceStatus.IN_PROGRESS: "In Progress",
    EvidenceStatus.DONE: "Done",
}
