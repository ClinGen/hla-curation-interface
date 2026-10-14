import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html


class HistoryTable(tables.Table):
    history_user = tables.Column(verbose_name="Changed By", orderable=False)
    history_type = tables.Column(verbose_name="Change", orderable=False)
    history_date = tables.DateTimeColumn(verbose_name="Date", format="Y-m-d H:i")

    class Meta:
        attrs = {"class": "table is-fullwidth is-hoverable"}
        empty_text = "No records."
        sequence = ("history_user", "history_type", "history_date")

    def __init__(
        self,
        *args,
        change_url_name: str = "",
        change_url_slug1: str | None = None,
        change_url_slug2: str | None = None,
        hide_user: bool = False,
        **kwargs,
    ) -> None:
        """Store change URL parameters before delegating to the parent.

        Args:
            *args: Positional arguments for the django-tables2 table.
            change_url_name: The URL name of the change-detail view.
            change_url_slug1: The first slug in the change-detail URL, if any.
            change_url_slug2: The second slug in the change-detail URL, if any.
            hide_user: Whether to drop the Changed By column, for public pages.
            **kwargs: Keyword arguments for the django-tables2 table.
        """
        if hide_user:
            kwargs["exclude"] = (*kwargs.get("exclude", ()), "history_user")
        super().__init__(*args, **kwargs)
        self.change_url_name = change_url_name
        self.change_url_slug1 = change_url_slug1
        self.change_url_slug2 = change_url_slug2

    def render_history_user(self, value: object) -> str:
        return str(value) if value else "------"

    def render_history_type(self, value: str, record: object) -> str:
        history_id = record.history_id  # type: ignore
        if self.change_url_slug2:
            url = reverse(
                self.change_url_name,
                args=[self.change_url_slug1, self.change_url_slug2, history_id],
            )
        elif self.change_url_slug1:
            url = reverse(
                self.change_url_name, args=[self.change_url_slug1, history_id]
            )
        else:
            url = reverse(self.change_url_name, args=[history_id])
        icon, label = {
            "Created": ("bi-file-plus", "Created"),
            "Changed": ("bi-pencil-square", "Updated"),
            "Deleted": ("bi-file-minus", "Deleted"),
        }.get(value, ("bi-question-circle", value))
        return format_html(
            '<a href="{}"><i class="bi {}"></i> {}</a>',
            url,
            icon,
            label,
        )
