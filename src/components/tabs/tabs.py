"""Provide the `tabs` component."""

from django_components import Component, register


@register("tabs")
class Tabs(Component):
    """Define the `tabs` component."""

    template_file = "tabs.html"

    def get_context_data(self, tabs: list) -> dict:
        """Return the context data for the template."""
        return {"tabs": tabs}
