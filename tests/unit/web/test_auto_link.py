"""Tests for automatic entity linking."""

from markupsafe import Markup

from nhl_scrabble.web.utils.auto_link import EntityLinker, auto_link


def test_auto_link_team_names() -> None:
    """Test linking team names."""
    entities = {
        "teams": [
            {"name": "Maple Leafs", "abbrev": "TOR"},
            {"name": "Canadiens", "abbrev": "MTL"},
        ],
    }
    linker = EntityLinker(entities)
    text = "The Maple Leafs beat the Canadiens 5-2."
    result = linker.link_text(text)
    assert '<a href="/teams/TOR">Maple Leafs</a>' in result
    assert '<a href="/teams/MTL">Canadiens</a>' in result


def test_auto_link_division_names() -> None:
    """Test linking division names."""
    entities = {
        "divisions": [
            {"name": "Atlantic"},
            {"name": "Metropolitan"},
        ],
    }
    linker = EntityLinker(entities)
    text = "Atlantic Division leads over Metropolitan."
    result = linker.link_text(text)
    assert '<a href="/divisions/Atlantic">Atlantic Division</a>' in result
    assert '<a href="/divisions/Metropolitan">Metropolitan</a>' in result


def test_auto_link_division_with_division_suffix() -> None:
    """Test linking division names with 'Division' suffix."""
    entities = {
        "divisions": [
            {"name": "Atlantic"},
        ],
    }
    linker = EntityLinker(entities)
    text = "The Atlantic Division is strong."
    result = linker.link_text(text)
    assert '<a href="/divisions/Atlantic">Atlantic Division</a>' in result


def test_auto_link_division_without_suffix() -> None:
    """Test linking division names without 'Division' suffix."""
    entities = {
        "divisions": [
            {"name": "Atlantic"},
        ],
    }
    linker = EntityLinker(entities)
    text = "The Atlantic is strong."
    result = linker.link_text(text)
    assert '<a href="/divisions/Atlantic">Atlantic</a>' in result


def test_auto_link_conference_names() -> None:
    """Test linking conference names."""
    entities = {
        "conferences": [
            {"name": "Eastern"},
            {"name": "Western"},
        ],
    }
    linker = EntityLinker(entities)
    text = "Eastern Conference and Western Conference compete."
    result = linker.link_text(text)
    assert '<a href="/conferences/Eastern">Eastern Conference</a>' in result
    assert '<a href="/conferences/Western">Western Conference</a>' in result


def test_auto_link_player_names() -> None:
    """Test linking player names with IDs."""
    entities = {
        "players": [
            {"name": "Connor McDavid", "id": 8478402},
            {"name": "Auston Matthews", "id": 8479318},
        ],
    }
    linker = EntityLinker(entities)
    text = "Connor McDavid and Auston Matthews are top players."
    result = linker.link_text(text)
    assert '<a href="/players/8478402">Connor McDavid</a>' in result
    assert '<a href="/players/8479318">Auston Matthews</a>' in result


def test_auto_link_player_without_id_not_linked() -> None:
    """Test that players without IDs are not linked."""
    entities = {
        "players": [
            {"name": "Unknown Player", "id": None},
        ],
    }
    linker = EntityLinker(entities)
    text = "Unknown Player is not linked."
    result = linker.link_text(text)
    assert '<a href="/players/' not in result
    assert "Unknown Player" in result


def test_auto_link_case_insensitive() -> None:
    """Test case-insensitive matching."""
    entities = {
        "teams": [{"name": "Maple Leafs", "abbrev": "TOR"}],
    }
    linker = EntityLinker(entities)
    text = "The maple leafs and MAPLE LEAFS are the same team."
    result = linker.link_text(text)
    # Should have 2 links (case-insensitive)
    assert result.count('<a href="/teams/TOR">') == 2


def test_auto_link_exclude_types() -> None:
    """Test excluding specific entity types."""
    entities = {
        "teams": [{"name": "Maple Leafs", "abbrev": "TOR"}],
        "divisions": [{"name": "Atlantic"}],
    }
    linker = EntityLinker(entities)
    text = "Maple Leafs play in Atlantic Division."
    result = linker.link_text(text, exclude_types=["team"])
    assert '<a href="/teams/TOR">Maple Leafs</a>' not in result
    assert '<a href="/divisions/Atlantic">Atlantic Division</a>' in result


def test_auto_link_no_partial_matches() -> None:
    """Test that partial words are not matched."""
    entities = {
        "divisions": [{"name": "Pacific"}],
    }
    linker = EntityLinker(entities)
    text = "Specifically, the Pacific Division is strong."
    result = linker.link_text(text)
    # "Specifically" should not be linked (contains "Pacific")
    assert result.count('<a href="/divisions/Pacific">') == 1
    assert "Specifically" in result
    # Ensure "Specifically" wasn't modified
    assert '<a href="/divisions/Pacific">Specifically' not in result


def test_auto_link_word_boundaries() -> None:
    """Test that word boundaries are respected."""
    entities = {
        "teams": [{"name": "Rangers", "abbrev": "NYR"}],
    }
    linker = EntityLinker(entities)
    text = "The Rangers are great, not the ex-Rangers."
    result = linker.link_text(text)
    # Both "Rangers" should be linked (word boundaries)
    assert result.count('<a href="/teams/NYR">Rangers</a>') == 2


def test_auto_link_jinja2_filter() -> None:
    """Test Jinja2 filter function."""
    entity_data = {
        "teams": [{"name": "Maple Leafs", "abbrev": "TOR"}],
    }
    text = "The Maple Leafs won!"
    result = auto_link(text, entity_data)
    assert isinstance(result, Markup)
    assert '<a href="/teams/TOR">Maple Leafs</a>' in result


def test_auto_link_jinja2_filter_with_markup_input() -> None:
    """Test Jinja2 filter with Markup input."""
    entity_data = {
        "teams": [{"name": "Maple Leafs", "abbrev": "TOR"}],
    }
    text = Markup("The Maple Leafs won!")
    result = auto_link(text, entity_data)
    assert isinstance(result, Markup)
    assert '<a href="/teams/TOR">Maple Leafs</a>' in result


def test_auto_link_jinja2_filter_with_exclude() -> None:
    """Test Jinja2 filter with exclusions."""
    entity_data = {
        "teams": [{"name": "Maple Leafs", "abbrev": "TOR"}],
        "divisions": [{"name": "Atlantic"}],
    }
    text = "Maple Leafs in Atlantic Division"
    result = auto_link(text, entity_data, exclude="team")
    assert '<a href="/teams/TOR">Maple Leafs</a>' not in result
    assert '<a href="/divisions/Atlantic">Atlantic Division</a>' in result


def test_auto_link_empty_entities() -> None:
    """Test with empty entity data."""
    entities: dict[str, list[dict[str, str | int]]] = {
        "teams": [],
        "divisions": [],
        "conferences": [],
        "players": [],
    }
    linker = EntityLinker(entities)
    text = "Some random text with no entities."
    result = linker.link_text(text)
    assert result == text
    assert "<a href=" not in result


def test_auto_link_multiple_entity_types() -> None:
    """Test linking multiple entity types in same text."""
    entities = {
        "teams": [{"name": "Maple Leafs", "abbrev": "TOR"}],
        "divisions": [{"name": "Atlantic"}],
        "conferences": [{"name": "Eastern"}],
        "players": [{"name": "Auston Matthews", "id": 8479318}],
    }
    linker = EntityLinker(entities)
    text = (
        "Auston Matthews leads the Maple Leafs in the Atlantic Division of the Eastern Conference."
    )
    result = linker.link_text(text)
    assert '<a href="/players/8479318">Auston Matthews</a>' in result
    assert '<a href="/teams/TOR">Maple Leafs</a>' in result
    assert '<a href="/divisions/Atlantic">Atlantic Division</a>' in result
    assert '<a href="/conferences/Eastern">Eastern Conference</a>' in result


def test_auto_link_preserves_original_case() -> None:
    """Test that linking preserves the original case in text."""
    entities = {
        "teams": [{"name": "Maple Leafs", "abbrev": "TOR"}],
    }
    linker = EntityLinker(entities)
    text = "The MAPLE LEAFS and maple leafs."
    result = linker.link_text(text)
    # Should preserve "MAPLE LEAFS" and "maple leafs" as they appear
    assert "MAPLE LEAFS" in result
    assert "maple leafs" in result
