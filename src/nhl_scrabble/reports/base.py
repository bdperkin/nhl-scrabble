"""Base reporter class for all report types."""

from abc import ABC, abstractmethod
from typing import Any


class BaseReporter(ABC):
    """Abstract base class for all reporters.

    All report generators should inherit from this class and implement
    the generate() method to produce their specific output format.
    """

    @abstractmethod
    def generate(self, data: Any) -> str:
        """Generate report output.

        Args:
            data: The data to generate a report from

        Returns:
            Formatted report string
        """
        pass

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
