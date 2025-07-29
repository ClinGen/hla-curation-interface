"""Houses constants shared by multiple models."""


class Status:
    """Defines the status codes for curations and evidence."""

    IN_PROGRESS = "INP"
    DONE = "DNE"


STATUS_CHOICES = {
    Status.IN_PROGRESS: "In Progress",
    Status.DONE: "Done",
}
