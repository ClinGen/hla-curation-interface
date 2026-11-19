"""Houses form widgets shared across apps."""

from django import forms
from django.urls import reverse


class SuggestInput(forms.TextInput):
    """A text input that suggests existing records as the curator types.

    common/form/input/text.html renders it as a combobox that fetches suggestions
    from the named URL, a SuggestView, with HTMX. The curator can still type a
    value that isn't suggested.
    """

    def __init__(self, url_name: str, attrs: dict | None = None) -> None:
        """Remembers which suggest view to ask.

        Args:
            url_name: The name of the SuggestView's URL, e.g., allele-suggest.
            attrs: HTML attributes for the input, as for TextInput.
        """
        super().__init__(attrs)
        self.url_name = url_name

    @property
    def suggest_url(self) -> str:
        """The suggest view's URL."""
        return reverse(self.url_name)
