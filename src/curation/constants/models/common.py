"""Houses constants shared by multiple models."""


class Status:
    """Defines the status codes for curations and evidence."""

    IN_PROGRESS = "INP"
    DONE = "DNE"
    READY_FOR_REVIEW = "RFR"
    PROVISIONAL = "PRO"
    PUBLISHED = "PUB"


STATUS_CHOICES = {
    Status.IN_PROGRESS: "In Progress",
    Status.DONE: "Done",
}

CURATION_STATUS_CHOICES = {
    Status.IN_PROGRESS: "In Progress",
    Status.READY_FOR_REVIEW: "Ready for Review",
    Status.PROVISIONAL: "Provisional",
    Status.PUBLISHED: "Published",
}

CURATION_STATUS_TRANSITIONS: dict[str, frozenset[str]] = {
    Status.IN_PROGRESS: frozenset({Status.READY_FOR_REVIEW}),
    Status.READY_FOR_REVIEW: frozenset({Status.IN_PROGRESS, Status.PROVISIONAL}),
    Status.PROVISIONAL: frozenset({Status.PUBLISHED}),
    Status.PUBLISHED: frozenset(),
}
