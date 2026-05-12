"""Unit tests for auto-linking utility.

This module tests the automatic entity linking functionality used in web templates to convert entity
names to clickable links.
"""

from __future__ import annotations

from markupsafe import Markup

from nhl_scrabble.web.utils.auto_link import EntityLinker, auto_link


class TestEntityLinker:
    """Test EntityLinker class."""

    def test_link_nationality(self) -> None:
        """Test linking nationality names."""
        entity_data = {
            "nationalities": [
                {"name": "Canada"},
                {"name": "United States"},
            ],
        }

        linker = EntityLinker(entity_data)
        result = linker.link_text("Players from Canada and United States")

        assert '<a href="/nationalities/Canada">Canada</a>' in result
        assert '<a href="/nationalities/United States">United States</a>' in result

    def test_link_nationality_case_insensitive(self) -> None:
        """Test nationality linking is case-insensitive."""
        entity_data = {
            "nationalities": [
                {"name": "Sweden"},
            ],
        }

        linker = EntityLinker(entity_data)
        result = linker.link_text("Players from sweden and SWEDEN")

        # Should link both mentions regardless of case
        assert result.count('<a href="/nationalities/Sweden">') == 2

    def test_exclude_nationality_linking(self) -> None:
        """Test excluding nationality from linking."""
        entity_data = {
            "nationalities": [
                {"name": "Russia"},
            ],
            "teams": [
                {"name": "Edmonton Oilers", "abbrev": "EDM"},
            ],
        }

        linker = EntityLinker(entity_data)
        result = linker.link_text(
            "Players from Russia play for Edmonton Oilers",
            exclude_types=["nationality"],
        )

        # Nationality should not be linked when excluded
        assert '<a href="/nationalities/Russia">' not in result
        # But team should still be linked
        assert '<a href="/teams/EDM">Edmonton Oilers</a>' in result

    def test_empty_entity_data(self) -> None:
        """Test with empty entity data."""
        linker = EntityLinker({})
        result = linker.link_text("Some text with no entities")

        assert result == "Some text with no entities"


class TestAutoLinkFunction:
    """Test auto_link Jinja2 filter function."""

    def test_auto_link_basic(self) -> None:
        """Test basic auto-linking."""
        entity_data = {
            "teams": [
                {"name": "Toronto Maple Leafs", "abbrev": "TOR"},
            ],
        }

        result = auto_link("Go Toronto Maple Leafs!", entity_data)

        assert isinstance(result, Markup)
        assert '<a href="/teams/TOR">Toronto Maple Leafs</a>' in result

    def test_auto_link_with_exclude(self) -> None:
        """Test auto_link with excluded entity types."""
        entity_data = {
            "teams": [
                {"name": "Boston Bruins", "abbrev": "BOS"},
            ],
            "players": [
                {"name": "Connor McDavid", "id": 8478402},
            ],
        }

        result = auto_link(
            "Connor McDavid played against Boston Bruins",
            entity_data,
            exclude="player",
        )

        # Player should not be linked
        assert '<a href="/players/' not in result
        # Team should be linked
        assert '<a href="/teams/BOS">Boston Bruins</a>' in result

    def test_auto_link_with_markup_input(self) -> None:
        """Test auto_link with Markup input."""
        entity_data = {
            "divisions": [
                {"name": "Atlantic"},
            ],
        }

        markup_text = Markup("Teams in the Atlantic division")
        result = auto_link(markup_text, entity_data)

        assert isinstance(result, Markup)
        # Verify Atlantic is linked (may include surrounding text in match)
        assert '<a href="/divisions/Atlantic">' in result
        assert "Atlantic" in result

    def test_auto_link_multiple_exclude(self) -> None:
        """Test excluding multiple entity types."""
        entity_data = {
            "teams": [
                {"name": "Montreal Canadiens", "abbrev": "MTL"},
            ],
            "divisions": [
                {"name": "Atlantic"},
            ],
            "conferences": [
                {"name": "Eastern"},
            ],
        }

        result = auto_link(
            "Montreal Canadiens in Atlantic division of Eastern conference",
            entity_data,
            exclude="division,conference",
        )

        # Team should be linked
        assert '<a href="/teams/MTL">Montreal Canadiens</a>' in result
        # Division and conference should not be linked
        assert '<a href="/divisions/' not in result
        assert '<a href="/conferences/' not in result
