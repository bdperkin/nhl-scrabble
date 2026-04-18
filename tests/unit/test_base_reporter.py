"""Tests for BaseReporter common utilities."""

from nhl_scrabble.reports.base import BaseReporter


class ConcreteReporter(BaseReporter):
    """Concrete implementation for testing."""

    def generate(self, data):
        """Return test output."""
        return "test"


class TestBaseReporter:
    """Tests for BaseReporter utility methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.reporter = ConcreteReporter()

    def test_format_header(self):
        """Test header formatting."""
        result = self.reporter._format_header("Test Header")
        assert "Test Header" in result
        assert "=" in result

    def test_format_header_custom_width(self):
        """Test header formatting with custom width."""
        result = self.reporter._format_header("Test", width=40)
        # Header should have separator line of 40 equals signs
        assert "=" * 40 in result

    def test_format_subheader(self):
        """Test subheader formatting."""
        result = self.reporter._format_subheader("Test Subheader")
        assert "Test Subheader" in result
        assert "-" in result

    def test_format_subheader_custom_width(self):
        """Test subheader formatting with custom width."""
        result = self.reporter._format_subheader("Test", width=30)
        # Subheader should have separator line of 30 dashes
        assert "-" * 30 in result

    def test_sort_by_key_ascending(self):
        """Test sorting items in ascending order."""
        items = [3, 1, 4, 1, 5, 9, 2, 6]
        result = self.reporter._sort_by_key(items, key=lambda x: x)
        assert result == [1, 1, 2, 3, 4, 5, 6, 9]

    def test_sort_by_key_descending(self):
        """Test sorting items in descending order."""
        items = [3, 1, 4, 1, 5, 9, 2, 6]
        result = self.reporter._sort_by_key(items, key=lambda x: x, reverse=True)
        assert result == [9, 6, 5, 4, 3, 2, 1, 1]

    def test_sort_by_key_with_objects(self):
        """Test sorting complex objects by key."""

        class Item:
            def __init__(self, score):
                self.score = score

        items = [Item(30), Item(10), Item(20)]
        result = self.reporter._sort_by_key(items, key=lambda x: x.score, reverse=True)
        assert result[0].score == 30
        assert result[1].score == 20
        assert result[2].score == 10

    def test_take_top_basic(self):
        """Test taking top N items."""
        items = [1, 2, 3, 4, 5]
        result = self.reporter._take_top(items, 3)
        assert result == [1, 2, 3]

    def test_take_top_more_than_available(self):
        """Test taking more items than available."""
        items = [1, 2, 3]
        result = self.reporter._take_top(items, 10)
        assert result == [1, 2, 3]

    def test_take_top_zero(self):
        """Test taking zero items."""
        items = [1, 2, 3]
        result = self.reporter._take_top(items, 0)
        assert result == []

    def test_take_top_empty_list(self):
        """Test taking from empty list."""
        items = []
        result = self.reporter._take_top(items, 5)
        assert result == []

    def test_paginate_basic(self):
        """Test basic pagination."""
        items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        pages = list(self.reporter._paginate(items, 3))
        assert len(pages) == 4
        assert pages[0] == [1, 2, 3]
        assert pages[1] == [4, 5, 6]
        assert pages[2] == [7, 8, 9]
        assert pages[3] == [10]

    def test_paginate_exact_fit(self):
        """Test pagination with exact fit."""
        items = [1, 2, 3, 4, 5, 6]
        pages = list(self.reporter._paginate(items, 2))
        assert len(pages) == 3
        assert pages[0] == [1, 2]
        assert pages[1] == [3, 4]
        assert pages[2] == [5, 6]

    def test_paginate_empty_list(self):
        """Test pagination of empty list."""
        items = []
        pages = list(self.reporter._paginate(items, 5))
        assert len(pages) == 0

    def test_paginate_single_page(self):
        """Test pagination when all items fit in one page."""
        items = [1, 2, 3]
        pages = list(self.reporter._paginate(items, 10))
        assert len(pages) == 1
        assert pages[0] == [1, 2, 3]

    def test_format_score_default_width(self):
        """Test score formatting with default width."""
        result = self.reporter._format_score(42)
        assert result == "  42"  # Default width is 4

    def test_format_score_custom_width(self):
        """Test score formatting with custom width."""
        result = self.reporter._format_score(42, width=6)
        assert result == "    42"

    def test_format_score_large_number(self):
        """Test score formatting with number larger than width."""
        result = self.reporter._format_score(12345, width=3)
        assert result == "12345"  # Width is minimum, not strict

    def test_format_score_zero(self):
        """Test score formatting with zero."""
        result = self.reporter._format_score(0)
        assert result == "   0"

    def test_format_average_default(self):
        """Test average formatting with defaults."""
        result = self.reporter._format_average(42.5)
        assert result == "42.50"  # Default: width=5, decimals=2

    def test_format_average_custom_decimals(self):
        """Test average formatting with custom decimals."""
        result = self.reporter._format_average(42.567, decimals=1)
        assert result == " 42.6"  # Rounded to 1 decimal

    def test_format_average_custom_width(self):
        """Test average formatting with custom width."""
        result = self.reporter._format_average(42.5, width=8, decimals=2)
        assert result == "   42.50"

    def test_format_average_zero(self):
        """Test average formatting with zero."""
        result = self.reporter._format_average(0.0)
        assert result == " 0.00"

    def test_format_average_large_number(self):
        """Test average formatting with large number."""
        result = self.reporter._format_average(12345.67, width=10, decimals=2)
        assert result == "  12345.67"

    def test_format_team_list_basic(self):
        """Test team list formatting."""
        teams = ["WSH", "NYR", "PIT"]
        result = self.reporter._format_team_list(teams)
        assert result == "NYR, PIT, WSH"  # Sorted alphabetically

    def test_format_team_list_unsorted(self):
        """Test team list formatting sorts teams."""
        teams = ["ZZZ", "AAA", "MMM"]
        result = self.reporter._format_team_list(teams)
        assert result == "AAA, MMM, ZZZ"

    def test_format_team_list_single_team(self):
        """Test team list formatting with single team."""
        teams = ["WSH"]
        result = self.reporter._format_team_list(teams)
        assert result == "WSH"

    def test_format_team_list_empty(self):
        """Test team list formatting with empty list."""
        teams = []
        result = self.reporter._format_team_list(teams)
        assert result == ""

    def test_format_team_list_duplicates(self):
        """Test team list formatting handles duplicates."""
        teams = ["WSH", "NYR", "WSH"]
        result = self.reporter._format_team_list(teams)
        # Should sort but keep duplicates
        assert result == "NYR, WSH, WSH"
