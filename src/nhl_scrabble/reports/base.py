"""Base reporter class for all report types."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Iterator
from typing import Any, TypeVar

T = TypeVar("T")


class BaseReporter(ABC):
    """Abstract base class for all reporters.

    All report generators should inherit from this class and implement the generate() method to
    produce their specific output format.

    The base class provides common utilities for:
    - Header and subheader formatting
    - Sorting and filtering data
    - Pagination and limiting results
    - Number formatting (scores, averages)
    - Team and player listing
    """

    @abstractmethod
    def generate(self, data: Any) -> str:
        """Generate report output.

        Args:
            data: The data to generate a report from

        Returns:
            Formatted report string
        """

    def _format_header(self, title: str, width: int = 80) -> str:
        """Format a section header.

        Args:
            title: Header title
            width: Total width of the header line

        Returns:
            Formatted header string
        """
        separator = "=" * width
        return f"\n{separator}\n\n{title}\n{separator}"

    def _format_subheader(self, title: str, width: int = 80) -> str:
        """Format a subsection header.

        Args:
            title: Subheader title
            width: Total width of the subheader line

        Returns:
            Formatted subheader string
        """
        separator = "-" * width
        return f"\n{title}\n{separator}"

    def _sort_by_key(
        self, items: Iterable[T], key: Callable[[T], Any], reverse: bool = False
    ) -> list[T]:
        """Sort items by a key function.

        Args:
            items: Items to sort
            key: Function to extract sort key from each item
            reverse: If True, sort in descending order (default: False)

        Returns:
            Sorted list of items
        """
        return sorted(items, key=key, reverse=reverse)

    def _take_top(self, items: list[T], n: int) -> list[T]:
        """Take the top N items from a list.

        Args:
            items: List of items (assumed to be already sorted)
            n: Number of items to take

        Returns:
            List containing up to N items
        """
        return items[:n]

    def _paginate(self, items: list[T], page_size: int) -> Iterator[list[T]]:
        """Paginate items into chunks.

        Args:
            items: List of items to paginate
            page_size: Number of items per page

        Yields:
            Pages containing up to page_size items
        """
        for i in range(0, len(items), page_size):
            yield items[i : i + page_size]

    def _format_score(self, value: int, width: int = 4) -> str:
        """Format a score value.

        Args:
            value: Score value to format
            width: Minimum field width (default: 4)

        Returns:
            Formatted score string
        """
        return f"{value:{width}}"

    def _format_average(self, value: float, width: int = 5, decimals: int = 2) -> str:
        """Format an average value.

        Args:
            value: Average value to format
            width: Minimum field width (default: 5)
            decimals: Number of decimal places (default: 2)

        Returns:
            Formatted average string
        """
        return f"{value:{width}.{decimals}f}"

    def _format_team_list(self, teams: list[str]) -> str:
        """Format a list of team abbreviations.

        Args:
            teams: List of team abbreviations

        Returns:
            Formatted team list string (sorted, comma-separated)
        """
        return ", ".join(sorted(teams))
