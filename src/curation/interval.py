"""Houses a custom interval class used in scoring."""

from decimal import Decimal


class Interval:
    """Defines an interval."""

    def __init__(
        self,
        *,
        start: Decimal,
        end: Decimal,
        start_inclusive: bool,
        end_inclusive: bool,
        variable: str,
    ) -> None:
        """Sets the interval's start, end, and variable."""
        self.start = start
        self.end = end
        self.start_inclusive = start_inclusive
        self.end_inclusive = end_inclusive
        self.variable = variable

    def __str__(self) -> str:
        """Returns a string representation of the object for the user."""
        start_operator = "≤" if self.start_inclusive else "<"
        end_operator = "≤" if self.end_inclusive else "<"

        if self.start == Decimal("Infinity"):
            start = "∞"
        elif self.start == Decimal("-Infinity"):
            start = "-∞"
        else:
            start = str(self.start)

        if self.end == Decimal("Infinity"):
            end = "∞"
        elif self.end == Decimal("-Infinity"):
            end = "-∞"
        else:
            end = str(self.end)

        return f"{start} {start_operator} {self.variable} {end_operator} {end}"

    def __repr__(self) -> str:
        """Returns a string representation of the object for the developer."""
        start_bracket = "[" if self.start_inclusive else "("
        end_bracket = "]" if self.end_inclusive else ")"
        return f"Interval({start_bracket}{self.start}, {self.end}{end_bracket})"

    def contains(self, number: Decimal) -> bool:
        """Returns whether the given number falls within the interval."""
        if self.start_inclusive:
            lower_bound_check = self.start <= number
        else:
            lower_bound_check = self.start < number

        if self.end_inclusive:
            upper_bound_check = number <= self.end
        else:
            upper_bound_check = number < self.end

        return lower_bound_check and upper_bound_check
