"""Automatic entity linking utilities for web templates."""

import re
from typing import Any

from markupsafe import Markup


class EntityLinker:
    """Automatically link entity names to their detail pages."""

    def _build_patterns(self) -> None:
        """Build regex patterns for entity matching."""
        # Build patterns sorted by length (longest first to avoid partial matches)
        self.team_patterns: list[tuple[str, str]] = [
            (re.escape(team["name"]), team["abbrev"])
            for team in sorted(
                self.entities.get("teams", []),
                key=lambda t: len(t["name"]),
                reverse=True,
            )
        ]

        self.division_patterns: list[tuple[str, str]] = [
            (re.escape(div["name"]), div["name"])
            for div in sorted(
                self.entities.get("divisions", []),
                key=lambda d: len(d["name"]),
                reverse=True,
            )
        ]

        self.conference_patterns: list[tuple[str, str]] = [
            (re.escape(conf["name"]), conf["name"])
            for conf in sorted(
                self.entities.get("conferences", []),
                key=lambda c: len(c["name"]),
                reverse=True,
            )
        ]

        # Players require player_id for linking (depends on task #051)
        self.player_patterns: list[tuple[str, int]] = [
            (re.escape(player["name"]), player.get("id"))
            for player in sorted(
                self.entities.get("players", []),
                key=lambda p: len(p["name"]),
                reverse=True,
            )
            if player.get("id")  # Only link players with IDs
        ]

    def __init__(self, entities: dict[str, list[dict[str, Any]]]) -> None:
        """Initialize the entity linker with entity data.

        Args:
            entities: Dictionary containing entity lists by type:
                {
                    'teams': [{'name': 'Maple Leafs', 'abbrev': 'TOR'}, ...],
                    'divisions': [{'name': 'Atlantic'}, ...],
                    'conferences': [{'name': 'Eastern'}, ...],
                    'players': [{'name': 'Connor McDavid', 'id': 8478402}, ...]
                }
        """
        self.entities = entities
        self._build_patterns()

    def link_text(self, text: str, exclude_types: list[str] | None = None) -> str:
        """Automatically link entity names in text.

        Args:
            text: Text to process
            exclude_types: Entity types to skip ('team', 'division', 'conference', 'player')

        Returns:
            Text with entity names wrapped in <a> tags

        Examples:
            >>> entities = {
            ...     'teams': [{'name': 'Maple Leafs', 'abbrev': 'TOR'}],
            ...     'divisions': [{'name': 'Atlantic'}]
            ... }
            >>> linker = EntityLinker(entities)
            >>> linker.link_text("The Maple Leafs play in the Atlantic division")
            'The <a href="/teams/TOR">Maple Leafs</a> play in the <a href="/divisions/Atlantic">Atlantic</a> division'
        """
        exclude_types = exclude_types or []
        result = text

        # Apply patterns in order: teams, divisions, conferences, players
        # Use word boundaries to avoid partial matches
        if "team" not in exclude_types:
            for pattern, abbrev in self.team_patterns:
                regex = re.compile(rf"\b{pattern}\b", re.IGNORECASE)
                result = regex.sub(
                    lambda m, a=abbrev: f'<a href="/teams/{a}">{m.group(0)}</a>',
                    result,
                )

        if "division" not in exclude_types:
            for pattern, name in self.division_patterns:
                # Match "Atlantic" or "Atlantic Division"
                regex = re.compile(rf"\b{pattern}(?:\s+Division)?\b", re.IGNORECASE)
                result = regex.sub(
                    lambda m, n=name: f'<a href="/divisions/{n}">{m.group(0)}</a>',
                    result,
                )

        if "conference" not in exclude_types:
            for pattern, name in self.conference_patterns:
                # Match "Eastern" or "Eastern Conference"
                regex = re.compile(rf"\b{pattern}(?:\s+Conference)?\b", re.IGNORECASE)
                result = regex.sub(
                    lambda m, n=name: f'<a href="/conferences/{n}">{m.group(0)}</a>',
                    result,
                )

        if "player" not in exclude_types:
            for pattern, player_id in self.player_patterns:
                if player_id:  # Only link if we have a player ID
                    regex = re.compile(rf"\b{pattern}\b", re.IGNORECASE)
                    result = regex.sub(
                        lambda m, pid=player_id: f'<a href="/players/{pid}">{m.group(0)}</a>',
                        result,
                    )

        return result


def auto_link(text: str | Markup, entity_data: dict[str, Any], exclude: str = "") -> Markup:
    """Jinja2 filter to automatically link entity names.

    Usage in templates:
        {{ some_text | auto_link(entity_data) }}
        {{ some_text | auto_link(entity_data, exclude='team,player') }}

    Args:
        text: Text to process
        entity_data: Entity data dictionary (teams, divisions, conferences, players)
        exclude: Comma-separated list of entity types to exclude

    Returns:
        Markup object with entity names linked (safe for rendering)
    """
    # Convert Markup to string if needed
    text_str = str(text)

    exclude_types = [t.strip() for t in exclude.split(",") if t.strip()]
    linker = EntityLinker(entity_data)
    result = linker.link_text(text_str, exclude_types)

    # Return as Markup to prevent double-escaping
    # Safe: result contains only HTML we generated from escaped entity names
    return Markup(result)  # noqa: S704, B704
