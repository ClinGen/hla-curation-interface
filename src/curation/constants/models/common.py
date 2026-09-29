"""Houses constants shared by multiple models."""


class Status:
    """Defines the status codes for curations and evidence."""

    IN_PROGRESS = "INP"
    DONE = "DNE"
    PROVISIONAL = "PRV"
    APPROVED = "APR"
    PUBLISHED = "PUB"


STATUS_CHOICES = {
    Status.IN_PROGRESS: "In Progress",
    Status.DONE: "Done",
}

CURATION_STATUS_CHOICES = {
    Status.IN_PROGRESS: "In Progress",
    Status.PROVISIONAL: "Provisional",
    Status.APPROVED: "Approved",
    Status.PUBLISHED: "Published",
}

CURATION_STATUS_TRANSITIONS: dict[str, frozenset[str]] = {
    Status.IN_PROGRESS: frozenset({Status.PROVISIONAL}),
    Status.PROVISIONAL: frozenset({Status.IN_PROGRESS, Status.APPROVED}),
    Status.APPROVED: frozenset({Status.PUBLISHED}),
    Status.PUBLISHED: frozenset(),
}
