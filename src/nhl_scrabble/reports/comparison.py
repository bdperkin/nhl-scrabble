"""Season comparison report generator."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, TypedDict

if TYPE_CHECKING:
    from nhl_scrabble.models.player import PlayerScore
    from nhl_scrabble.models.team import TeamScore

logger = logging.getLogger(__name__)


class SeasonData(TypedDict):
    """Type definition for season data dictionary.

    Attributes:
        teams: Dictionary of team abbreviations to team scores
        players: List of all player scores
        total_score: Total score for all players
        team_count: Number of teams
        player_count: Number of players
    """

    teams: dict[str, TeamScore]
    players: list[PlayerScore]
    total_score: int
    team_count: int  # Used in TypedDict
    player_count: int  # Used in TypedDict


class SeasonComparison:
    """Compare NHL Scrabble scores across multiple seasons.

    This class provides functionality to compare team and player scores
    across different NHL seasons to identify trends and changes.

    Examples:
        >>> comparison = SeasonComparison(["20222023", "20232024"])
        >>> comparison.add_season_data("20222023", teams_2022, players_2022)
        >>> comparison.add_season_data("20232024", teams_2023, players_2023)
        >>> report = comparison.generate_report()
    """

    def __init__(self, seasons: list[str]) -> None:
        """Initialize season comparison.

        Args:
            seasons: List of season identifiers to compare (e.g., ['20222023', '20232024'])

        Examples:
            >>> comparison = SeasonComparison(["20222023", "20232024"])
            >>> len(comparison.seasons)
            2
        """
        self.seasons = sorted(seasons)
        self.season_data: dict[str, SeasonData] = {}
        logger.debug(f"Initialized comparison for {len(seasons)} seasons")

    def add_season_data(
        self,
        season: str,
        team_scores: dict[str, TeamScore],
        all_players: list[PlayerScore],
    ) -> None:
        """Add data for a specific season.

        Args:
            season: Season identifier (e.g., '20222023')
            team_scores: Dictionary of team scores for the season
            all_players: List of all player scores for the season

        Examples:
            >>> comparison = SeasonComparison(["20222023"])
            >>> comparison.add_season_data("20222023", {}, [])
            >>> "20222023" in comparison.season_data
            True
        """
        self.season_data[season] = {
            "teams": team_scores,
            "players": all_players,
            "total_score": sum(p.full_score for p in all_players),
            "team_count": len(team_scores),
            "player_count": len(all_players),
        }
        logger.debug(
            f"Added data for season {season}: {len(team_scores)} teams, {len(all_players)} players"
        )

    def generate_text_report(self) -> str:
        """Generate a text comparison report.

        Returns:
            Formatted text report comparing all seasons

        Examples:
            >>> comparison = SeasonComparison(["20222023", "20232024"])
            >>> report = comparison.generate_text_report()
            >>> "Season Comparison" in report
            True
        """
        lines = []
        lines.append("=" * 80)
        lines.append("NHL SCRABBLE SEASON COMPARISON")
        lines.append("=" * 80)
        lines.append("")

        # Overview section
        lines.append("OVERVIEW")
        lines.append("-" * 80)
        lines.append(f"Seasons compared: {', '.join(self.seasons)}")
        lines.append("")

        # Per-season statistics
        lines.append("SEASON STATISTICS")
        lines.append("-" * 80)
        for season in self.seasons:
            if season not in self.season_data:
                lines.append(f"{season}: No data available")
                continue

            data = self.season_data[season]
            lines.append(f"\nSeason {season}:")
            lines.append(f"  Teams: {data['team_count']}")
            lines.append(f"  Players: {data['player_count']}")
            lines.append(f"  Total Score: {data['total_score']:,}")
            if data["player_count"] > 0:
                avg_score = data["total_score"] / data["player_count"]
                lines.append(f"  Average per Player: {avg_score:.2f}")

        lines.append("")

        # Team comparison section (top teams by season)
        lines.append("TOP TEAMS BY SEASON")
        lines.append("-" * 80)
        for season in self.seasons:
            if season not in self.season_data:
                continue

            data = self.season_data[season]
            teams = data["teams"]

            # Sort teams by total score
            sorted_teams = sorted(
                teams.items(), key=lambda x: (x[1].total, x[1].avg_per_player), reverse=True
            )[:5]

            lines.append(f"\n{season} Top 5:")
            for rank, (abbrev, team) in enumerate(sorted_teams, 1):
                lines.append(
                    f"  {rank}. {abbrev:4} - {team.total:6,} points "
                    f"({team.player_count} players, avg: {team.avg_per_player:.2f})"
                )

        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    def generate_json_report(self) -> dict[str, Any]:
        """Generate a JSON comparison report.

        Returns:
            Dictionary containing comparison data

        Examples:
            >>> comparison = SeasonComparison(["20222023"])
            >>> report = comparison.generate_json_report()
            >>> "seasons" in report
            True
        """
        comparison_data: dict[str, Any] = {}

        for season in self.seasons:
            if season not in self.season_data:
                comparison_data[season] = {"error": "No data available"}
                continue

            data = self.season_data[season]
            comparison_data[season] = {
                "team_count": data["team_count"],
                "player_count": data["player_count"],
                "total_score": data["total_score"],
                "average_per_player": (
                    data["total_score"] / data["player_count"] if data["player_count"] > 0 else 0
                ),
            }

        return {
            "seasons": self.seasons,
            "comparison": comparison_data,
        }


class TrendAnalysis:
    """Analyze NHL Scrabble score trends across seasons.

    This class provides functionality to analyze how scores change
    over time and identify trends.

    Examples:
        >>> analysis = TrendAnalysis("20202021", "20232024")
        >>> analysis.add_season_data("20202021", teams_2020, players_2020)
        >>> trends = analysis.calculate_trends()
    """

    def __init__(self, start_season: str, end_season: str) -> None:
        """Initialize trend analysis.

        Args:
            start_season: Starting season (e.g., '20202021')
            end_season: Ending season (e.g., '20232024')

        Examples:
            >>> analysis = TrendAnalysis("20202021", "20232024")
            >>> analysis.start_season
            '20202021'
        """
        self.start_season = start_season
        self.end_season = end_season
        self.season_data: dict[str, SeasonData] = {}
        logger.debug(f"Initialized trend analysis from {start_season} to {end_season}")

    def add_season_data(
        self,
        season: str,
        team_scores: dict[str, TeamScore],
        all_players: list[PlayerScore],
    ) -> None:
        """Add data for a specific season.

        Args:
            season: Season identifier (e.g., '20222023')
            team_scores: Dictionary of team scores for the season
            all_players: List of all player scores for the season

        Examples:
            >>> analysis = TrendAnalysis("20202021", "20232024")
            >>> analysis.add_season_data("20222023", {}, [])
            >>> "20222023" in analysis.season_data
            True
        """
        self.season_data[season] = {
            "teams": team_scores,
            "players": all_players,
            "total_score": sum(p.full_score for p in all_players),
            "team_count": len(team_scores),
            "player_count": len(all_players),
        }
        logger.debug(f"Added data for season {season}")

    def calculate_trends(self) -> dict[str, Any]:
        """Calculate trends across all seasons.

        Returns:
            Dictionary containing trend analysis results

        Examples:
            >>> analysis = TrendAnalysis("20202021", "20232024")
            >>> trends = analysis.calculate_trends()
            >>> "seasons_analyzed" in trends
            True
        """
        sorted_seasons = sorted(self.season_data.keys())

        if len(sorted_seasons) < 2:
            return {
                "seasons_analyzed": len(sorted_seasons),
                "error": "Need at least 2 seasons for trend analysis",
            }

        # Calculate average scores per season
        averages = []
        for season in sorted_seasons:
            data = self.season_data[season]
            if data["player_count"] > 0:
                avg = data["total_score"] / data["player_count"]
                averages.append(avg)

        # Calculate trend direction
        if len(averages) >= 2:
            first_avg = averages[0]
            last_avg = averages[-1]
            change = last_avg - first_avg
            change_pct = (change / first_avg * 100) if first_avg > 0 else 0

            trend_direction = (
                "increasing" if change > 0 else "decreasing" if change < 0 else "stable"
            )
        else:
            change = 0
            change_pct = 0
            trend_direction = "unknown"

        return {
            "seasons_analyzed": len(sorted_seasons),
            "season_range": f"{sorted_seasons[0]} to {sorted_seasons[-1]}",
            "average_scores": averages,
            "trend_direction": trend_direction,
            "total_change": change,
            "percent_change": change_pct,
        }

    def generate_text_report(self) -> str:
        """Generate a text trend analysis report.

        Returns:
            Formatted text report

        Examples:
            >>> analysis = TrendAnalysis("20202021", "20232024")
            >>> report = analysis.generate_text_report()
            >>> "Trend Analysis" in report
            True
        """
        trends = self.calculate_trends()

        lines = []
        lines.append("=" * 80)
        lines.append("NHL SCRABBLE TREND ANALYSIS")
        lines.append("=" * 80)
        lines.append("")

        lines.append(f"Season Range: {self.start_season} to {self.end_season}")
        lines.append(f"Seasons Analyzed: {trends['seasons_analyzed']}")
        lines.append("")

        if "error" in trends:
            lines.append(f"Error: {trends['error']}")
        else:
            lines.append(f"Trend Direction: {trends['trend_direction'].upper()}")
            lines.append(f"Total Change: {trends['total_change']:.2f} points")
            lines.append(f"Percent Change: {trends['percent_change']:.2f}%")
            lines.append("")

            lines.append("SEASON AVERAGES:")
            lines.append("-" * 80)
            for i, season in enumerate(sorted(self.season_data.keys())):
                if i < len(trends["average_scores"]):
                    avg = trends["average_scores"][i]
                    lines.append(f"  {season}: {avg:.2f} points per player")

        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)
