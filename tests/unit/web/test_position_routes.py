"""Tests for position-related routes."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from nhl_scrabble.web.app import app


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client for the web app.

    Returns:
        TestClient instance
    """
    return TestClient(app)


@pytest.fixture
def mock_analysis_data() -> dict:
    """Create mock analysis data for testing.

    Returns:
        Mock analysis data with player and position information
    """
    return {
        "timestamp": "2024-05-09T12:00:00",
        "top_players": [
            {
                "player_id": 8478402,
                "full_name": "Connor McDavid",
                "first_name": "Connor",
                "last_name": "McDavid",
                "team": "EDM",
                "team_name": "Edmonton Oilers",
                "division": "Pacific",
                "conference": "Western",
                "score": 24,
                "first_score": 12,
                "last_score": 12,
                "birthplace": "Richmond Hill, ON",
                "birth_country": "CAN",
                "nationality": "CAN",
                "position_code": "C",
                "position": "Center",
                "position_type": "Forward",
            },
            {
                "player_id": 8477934,
                "full_name": "Auston Matthews",
                "first_name": "Auston",
                "last_name": "Matthews",
                "team": "TOR",
                "team_name": "Toronto Maple Leafs",
                "division": "Atlantic",
                "conference": "Eastern",
                "score": 22,
                "first_score": 11,
                "last_score": 11,
                "birthplace": "Scottsdale, AZ",
                "birth_country": "USA",
                "nationality": "USA",
                "position_code": "C",
                "position": "Center",
                "position_type": "Forward",
            },
            {
                "player_id": 8477492,
                "full_name": "Cale Makar",
                "first_name": "Cale",
                "last_name": "Makar",
                "team": "COL",
                "team_name": "Colorado Avalanche",
                "division": "Central",
                "conference": "Western",
                "score": 18,
                "first_score": 9,
                "last_score": 9,
                "birthplace": "Calgary, AB",
                "birth_country": "CAN",
                "nationality": "CAN",
                "position_code": "D",
                "position": "Defense",
                "position_type": "Defense",
            },
            {
                "player_id": 8471214,
                "full_name": "Carey Price",
                "first_name": "Carey",
                "last_name": "Price",
                "team": "MTL",
                "team_name": "Montreal Canadiens",
                "division": "Atlantic",
                "conference": "Eastern",
                "score": 15,
                "first_score": 8,
                "last_score": 7,
                "birthplace": "Anahim Lake, BC",
                "birth_country": "CAN",
                "nationality": "CAN",
                "position_code": "G",
                "position": "Goalie",
                "position_type": "Goalie",
            },
            {
                "player_id": 8480012,
                "full_name": "Kirill Kaprizov",
                "first_name": "Kirill",
                "last_name": "Kaprizov",
                "team": "MIN",
                "team_name": "Minnesota Wild",
                "division": "Central",
                "conference": "Western",
                "score": 20,
                "first_score": 10,
                "last_score": 10,
                "birthplace": "Novokuznetsk",
                "birth_country": "RUS",
                "nationality": "RUS",
                "position_code": "L",
                "position": "Left Wing",
                "position_type": "Forward",
            },
            {
                "player_id": 8479318,
                "full_name": "Mitch Marner",
                "first_name": "Mitch",
                "last_name": "Marner",
                "team": "TOR",
                "team_name": "Toronto Maple Leafs",
                "division": "Atlantic",
                "conference": "Eastern",
                "score": 19,
                "first_score": 9,
                "last_score": 10,
                "birthplace": "Markham, ON",
                "birth_country": "CAN",
                "nationality": "CAN",
                "position_code": "R",
                "position": "Right Wing",
                "position_type": "Forward",
            },
        ],
        "stats": {
            "total_players": 6,
            "highest_score": 24,
            "lowest_score": 15,
            "avg_score": 19.67,
            "highest_player_name": "Connor McDavid",
        },
    }


# ========================================
# Tests for /positions endpoint
# ========================================


@patch("nhl_scrabble.web.routes.positions.analyze_post", new_callable=AsyncMock)
def test_positions_page_loads(
    mock_analyze: AsyncMock,
    test_client: TestClient,
    mock_analysis_data: dict,
) -> None:
    """Test that positions page loads successfully.

    Args:
        mock_analyze: Mock async analysis endpoint
        test_client: Test client fixture
        mock_analysis_data: Mock analysis data
    """
    mock_analyze.return_value = mock_analysis_data

    response = test_client.get("/positions")

    assert response.status_code == 200
    assert b"positions" in response.content.lower()
    # Should show position types
    assert b"forward" in response.content.lower() or b"center" in response.content.lower()


@patch("nhl_scrabble.web.routes.positions.analyze_post", new_callable=AsyncMock)
def test_positions_page_shows_position_statistics(
    mock_analyze: AsyncMock,
    test_client: TestClient,
    mock_analysis_data: dict,
) -> None:
    """Test that positions page displays position statistics.

    Args:
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
        mock_analysis_data: Mock analysis data
    """
    mock_analyze.return_value = mock_analysis_data

    response = test_client.get("/positions")

    assert response.status_code == 200
    # Should have position statistics
    assert b"Connor McDavid" in response.content or b"McDavid" in response.content


@patch("nhl_scrabble.web.routes.positions.analyze_post", new_callable=AsyncMock)
def test_positions_page_nhl_api_error(
    mock_analyze: AsyncMock,
    test_client: TestClient,
) -> None:
    """Test handling of NHL API errors on positions page.

    Args:
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
    """
    from nhl_scrabble.api import NHLApiError

    mock_analyze.side_effect = NHLApiError("API failed")

    response = test_client.get("/positions")

    assert response.status_code == 500


@patch("nhl_scrabble.web.routes.positions.analyze_post", new_callable=AsyncMock)
def test_positions_page_empty_standings(
    mock_analyze: AsyncMock,
    test_client: TestClient,
) -> None:
    """Test positions page with empty position standings.

    Args:
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
    """
    # Mock data with no position information
    mock_data = {
        "timestamp": "2024-05-09T12:00:00",
        "top_players": [
            {
                "player_id": 8478402,
                "full_name": "Connor McDavid",
                "first_name": "Connor",
                "last_name": "McDavid",
                "team": "EDM",
                "score": 24,
                "first_score": 12,
                "last_score": 12,
                "division": "",
                "conference": "",
                "birthplace": "",
                "birth_country": "",
                "nationality": "",
                "position_code": "",  # Empty position
                "position": "",
                "position_type": "",
            },
        ],
        "stats": {
            "total_players": 1,
        },
    }
    mock_analyze.return_value = mock_data

    response = test_client.get("/positions")

    # Should still load successfully even with empty positions
    assert response.status_code == 200


def test_positions_page_templates_not_configured(test_client: TestClient) -> None:
    """Test error handling when templates are not configured.

    Args:
        test_client: Test client fixture
    """
    # Temporarily remove templates from app state
    original_templates = app.state.templates
    app.state.templates = None

    try:
        response = test_client.get("/positions")
        assert response.status_code == 500
        assert b"Templates not configured" in response.content
    finally:
        # Restore templates
        app.state.templates = original_templates


# ========================================
# Tests for /positions/{position_type} endpoint
# ========================================


@pytest.mark.parametrize(
    "position_type",
    ["Forward", "Defense", "Goalie"],
)
@patch("nhl_scrabble.web.routes.positions.analyze_post", new_callable=AsyncMock)
def test_position_type_page_loads(
    mock_analyze: AsyncMock,
    test_client: TestClient,
    mock_analysis_data: dict,
    position_type: str,
) -> None:
    """Test that position type pages load successfully.

    Args:
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
        mock_analysis_data: Mock analysis data
        position_type: Position type to test
    """
    mock_analyze.return_value = mock_analysis_data

    response = test_client.get(f"/positions/{position_type}")

    assert response.status_code == 200
    assert position_type.encode() in response.content


@patch("nhl_scrabble.web.routes.positions.analyze_post", new_callable=AsyncMock)
def test_position_type_page_invalid_type(
    mock_analyze: AsyncMock,
    test_client: TestClient,
    mock_analysis_data: dict,
) -> None:
    """Test 404 for invalid position type.

    Args:
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
        mock_analysis_data: Mock analysis data
    """
    mock_analyze.return_value = mock_analysis_data

    response = test_client.get("/positions/InvalidType")

    assert response.status_code == 404
    assert b"Invalid position type" in response.content


@patch("nhl_scrabble.web.routes.positions.analyze_post", new_callable=AsyncMock)
def test_position_type_page_no_players_found(
    mock_analyze: AsyncMock,
    test_client: TestClient,
) -> None:
    """Test 404 when no players found for position type.

    Args:
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
    """
    # Mock data with no players matching the position type
    mock_data = {
        "timestamp": "2024-05-09T12:00:00",
        "top_players": [
            {
                "player_id": 8478402,
                "full_name": "Connor McDavid",
                "first_name": "Connor",
                "last_name": "McDavid",
                "team": "EDM",
                "score": 24,
                "first_score": 12,
                "last_score": 12,
                "position_code": "C",
                "position": "Center",
                "position_type": "Forward",  # Only Forwards, no Defense
            },
        ],
        "stats": {},
    }
    mock_analyze.return_value = mock_data

    # Request Defense position type (which has no players)
    response = test_client.get("/positions/Defense")

    assert response.status_code == 404
    assert b"No players found for position type" in response.content


@patch("nhl_scrabble.web.routes.positions.analyze_post", new_callable=AsyncMock)
def test_position_type_page_shows_team_distribution(
    mock_analyze: AsyncMock,
    test_client: TestClient,
    mock_analysis_data: dict,
) -> None:
    """Test that position type page shows team distribution.

    Args:
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
        mock_analysis_data: Mock analysis data
    """
    mock_analyze.return_value = mock_analysis_data

    response = test_client.get("/positions/Forward")

    assert response.status_code == 200
    # Should show team information
    assert b"EDM" in response.content or b"TOR" in response.content


@patch("nhl_scrabble.web.routes.positions.analyze_post", new_callable=AsyncMock)
def test_position_type_page_nhl_api_error(
    mock_analyze: AsyncMock,
    test_client: TestClient,
) -> None:
    """Test handling of NHL API errors on position type page.

    Args:
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
    """
    from nhl_scrabble.api import NHLApiError

    mock_analyze.side_effect = NHLApiError("API failed")

    response = test_client.get("/positions/Forward")

    assert response.status_code == 500


def test_position_type_page_templates_not_configured(test_client: TestClient) -> None:
    """Test error handling when templates are not configured.

    Args:
        test_client: Test client fixture
    """
    original_templates = app.state.templates
    app.state.templates = None

    try:
        response = test_client.get("/positions/Forward")
        assert response.status_code == 500
        assert b"Templates not configured" in response.content
    finally:
        app.state.templates = original_templates


# ========================================
# Tests for /positions/detail/{position_code} endpoint
# ========================================


@pytest.mark.parametrize(
    ("position_code", "expected_name"),
    [
        ("C", b"Center"),
        ("L", b"Left Wing"),
        ("R", b"Right Wing"),
        ("D", b"Defense"),
        ("G", b"Goalie"),
    ],
)
@patch("nhl_scrabble.web.routes.positions.analyze_post", new_callable=AsyncMock)
def test_position_detail_page_loads(
    mock_analyze: AsyncMock,
    test_client: TestClient,
    mock_analysis_data: dict,
    position_code: str,
    expected_name: bytes,
) -> None:
    """Test that position detail pages load successfully.

    Args:
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
        mock_analysis_data: Mock analysis data
        position_code: Position code to test
        expected_name: Expected position name in response
    """
    mock_analyze.return_value = mock_analysis_data

    response = test_client.get(f"/positions/detail/{position_code}")

    assert response.status_code == 200
    assert expected_name in response.content


@pytest.mark.parametrize(
    "position_code",
    ["c", "l", "r", "d", "g"],  # Lowercase variants
)
@patch("nhl_scrabble.web.routes.positions.analyze_post", new_callable=AsyncMock)
def test_position_detail_page_case_insensitive(
    mock_analyze: AsyncMock,
    test_client: TestClient,
    mock_analysis_data: dict,
    position_code: str,
) -> None:
    """Test that position codes are case-insensitive.

    Args:
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
        mock_analysis_data: Mock analysis data
        position_code: Lowercase position code to test
    """
    mock_analyze.return_value = mock_analysis_data

    response = test_client.get(f"/positions/detail/{position_code}")

    assert response.status_code == 200


@patch("nhl_scrabble.web.routes.positions.analyze_post", new_callable=AsyncMock)
def test_position_detail_page_invalid_code(
    mock_analyze: AsyncMock,
    test_client: TestClient,
    mock_analysis_data: dict,
) -> None:
    """Test 404 for invalid position code.

    Args:
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
        mock_analysis_data: Mock analysis data
    """
    mock_analyze.return_value = mock_analysis_data

    response = test_client.get("/positions/detail/X")

    assert response.status_code == 404
    assert b"Invalid position code" in response.content


@patch("nhl_scrabble.web.routes.positions.analyze_post", new_callable=AsyncMock)
def test_position_detail_page_no_players_found(
    mock_analyze: AsyncMock,
    test_client: TestClient,
) -> None:
    """Test 404 when no players found for position code.

    Args:
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
    """
    # Mock data with no players at Right Wing position
    mock_data = {
        "timestamp": "2024-05-09T12:00:00",
        "top_players": [
            {
                "player_id": 8478402,
                "full_name": "Connor McDavid",
                "first_name": "Connor",
                "last_name": "McDavid",
                "team": "EDM",
                "score": 24,
                "first_score": 12,
                "last_score": 12,
                "nationality": "CAN",
                "position_code": "C",  # Only Centers, no Right Wings
                "position": "Center",
                "position_type": "Forward",
            },
        ],
        "stats": {},
    }
    mock_analyze.return_value = mock_data

    # Request Right Wing position (which has no players)
    response = test_client.get("/positions/detail/R")

    assert response.status_code == 404
    assert b"No players found for position code" in response.content


@patch("nhl_scrabble.web.routes.positions.analyze_post", new_callable=AsyncMock)
def test_position_detail_page_shows_statistics(
    mock_analyze: AsyncMock,
    test_client: TestClient,
    mock_analysis_data: dict,
) -> None:
    """Test that position detail page shows position statistics.

    Args:
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
        mock_analysis_data: Mock analysis data
    """
    mock_analyze.return_value = mock_analysis_data

    response = test_client.get("/positions/detail/C")

    assert response.status_code == 200
    # Should show top player at center position
    assert b"Connor McDavid" in response.content or b"Auston Matthews" in response.content


@patch("nhl_scrabble.web.routes.positions.analyze_post", new_callable=AsyncMock)
def test_position_detail_page_shows_team_distribution(
    mock_analyze: AsyncMock,
    test_client: TestClient,
    mock_analysis_data: dict,
) -> None:
    """Test that position detail page shows team distribution.

    Args:
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
        mock_analysis_data: Mock analysis data
    """
    mock_analyze.return_value = mock_analysis_data

    response = test_client.get("/positions/detail/C")

    assert response.status_code == 200
    # Should show team information
    assert b"EDM" in response.content or b"TOR" in response.content


@patch("nhl_scrabble.web.routes.positions.analyze_post", new_callable=AsyncMock)
def test_position_detail_page_nhl_api_error(
    mock_analyze: AsyncMock,
    test_client: TestClient,
) -> None:
    """Test handling of NHL API errors on position detail page.

    Args:
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
    """
    from nhl_scrabble.api import NHLApiError

    mock_analyze.side_effect = NHLApiError("API failed")

    response = test_client.get("/positions/detail/C")

    assert response.status_code == 500


def test_position_detail_page_templates_not_configured(test_client: TestClient) -> None:
    """Test error handling when templates are not configured.

    Args:
        test_client: Test client fixture
    """
    original_templates = app.state.templates
    app.state.templates = None

    try:
        response = test_client.get("/positions/detail/C")
        assert response.status_code == 500
        assert b"Templates not configured" in response.content
    finally:
        app.state.templates = original_templates
