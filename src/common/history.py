"""Provides a hacky function for getting human-readable history diffs."""

from typing import Any

from django.core.exceptions import FieldDoesNotExist
from django.db import models


def resolve_changes(
    model_class: type[models.Model],
    record: Any,  # noqa
    prev_record: Any,  # noqa
) -> list[dict[str, Any]] | None:
    """Returns a human-readable diff between two history records.

    Returns `None` when there is no previous record (i.e. this is the creation
    record). Otherwise, returns a list of dicts with keys `field`, `old`,
    and `new`, using `verbose_name` for the field label and the choice display
    value for fields that define choices.
    """
    if not prev_record:
        return None
    result = []
    for change in record.diff_against(prev_record).changes:
        label: str = change.field
        old_val: Any = change.old
        new_val: Any = change.new
        try:
            field: models.Field | None = None
            try:
                field = model_class._meta.get_field(change.field)  # type: ignore # noqa
            except FieldDoesNotExist:
                if change.field.endswith("_id"):
                    field = model_class._meta.get_field(change.field[:-3])  # type: ignore # noqa
            if field is not None:
                label = str(getattr(field, "verbose_name", field.name))
                choices = dict(getattr(field, "choices", None) or [])
                if choices:
                    old_val = choices.get(change.old, change.old)
                    new_val = choices.get(change.new, change.new)
        except Exception:  # noqa
            pass
        result.append({"field": label, "old": old_val, "new": new_val})
    return result
