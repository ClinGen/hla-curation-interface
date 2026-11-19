"""Houses form widgets shared across apps."""

import re

from django import forms
from django.urls import reverse


class SuggestInput(forms.TextInput):
    """A text input that suggests existing records as the curator types.

    common/form/input/text.html renders it as a combobox that fetches suggestions
    from the named URL, a SuggestView, with HTMX. The curator can still type a
    value that isn't suggested.
    """

    def __init__(
        self,
        url_name: str,
        *,
        separators: re.Pattern | None = None,
        attrs: dict | None = None,
    ) -> None:
        """Remembers which suggest view to ask.

        Args:
            url_name: The name of the SuggestView's URL, e.g., allele-suggest.
            separators: For an input that holds a list, the pattern between its
                items. Then only the item being typed is suggested and replaced.
            attrs: HTML attributes for the input, as for TextInput.
        """
        super().__init__(attrs)
        self.url_name = url_name
        self.separators = separators.pattern if separators else ""

    @property
    def suggest_url(self) -> str:
        """The suggest view's URL."""
        return reverse(self.url_name)
