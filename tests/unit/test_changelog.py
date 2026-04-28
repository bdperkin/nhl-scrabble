"""Tests for changelog configuration and generation.

This module contains tests for validating the git-cliff configuration used for automated
CHANGELOG.md generation.
"""

from pathlib import Path


def test_cliff_config_exists() -> None:
    """Test that cliff.toml configuration exists."""
    cliff_config = Path(".cliff.toml")
    assert cliff_config.exists(), "Expected .cliff.toml configuration file to exist"


def test_cliff_config_valid() -> None:
    """Test that cliff.toml is valid TOML."""
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        import tomli as tomllib  # Fallback for Python <3.11

    cliff_config = Path(".cliff.toml")
    with cliff_config.open("rb") as f:
        config = tomllib.load(f)

    # Validate required sections exist
    assert "changelog" in config, "Expected 'changelog' section in config"
    assert "git" in config, "Expected 'git' section in config"


def test_conventional_commits_enabled() -> None:
    """Test that conventional commits parsing is enabled."""
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        import tomli as tomllib  # Fallback for Python <3.11

    cliff_config = Path(".cliff.toml")
    with cliff_config.open("rb") as f:
        config = tomllib.load(f)

    # Verify conventional commits are enabled
    assert (
        config["git"]["conventional_commits"] is True
    ), "Expected conventional_commits to be enabled in git-cliff config"


def test_commit_parsers_configured() -> None:
    """Test that commit parsers are properly configured for Keep a Changelog categories."""
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        import tomli as tomllib  # Fallback for Python <3.11

    cliff_config = Path(".cliff.toml")
    with cliff_config.open("rb") as f:
        config = tomllib.load(f)

    # Get commit parsers
    commit_parsers = config["git"]["commit_parsers"]
    assert isinstance(commit_parsers, list), "Expected commit_parsers to be a list"
    assert len(commit_parsers) > 0, "Expected at least one commit parser"

    # Extract parser mappings
    parser_map = {}
    skip_types = []
    for parser in commit_parsers:
        message_pattern = parser.get("message", "")
        if parser.get("skip"):
            # Extract commit type from pattern (e.g., "^feat" -> "feat")
            commit_type = message_pattern.replace("^", "")
            skip_types.append(commit_type)
        elif "group" in parser:
            commit_type = message_pattern.replace("^", "")
            parser_map[commit_type] = parser["group"]

    # Verify Keep a Changelog category mappings
    expected_mappings = {
        "feat": "Added",
        "fix": "Fixed",
        "refactor": "Changed",
        "perf": "Performance",
        "docs": "Documentation",
        "doc": "Documentation",
        "deprecate": "Deprecated",
        "remove": "Removed",
        "security": "Security",
    }

    for commit_type, expected_group in expected_mappings.items():
        assert commit_type in parser_map, f"Expected commit type '{commit_type}' to be configured"
        assert parser_map[commit_type] == expected_group, (
            f"Expected '{commit_type}' to map to '{expected_group}', "
            f"got '{parser_map[commit_type]}'"
        )

    # Verify CI/chore commits are skipped
    expected_skips = ["style", "test", "chore", "ci", "build"]
    for skip_type in expected_skips:
        assert skip_type in skip_types, f"Expected commit type '{skip_type}' to be skipped"


def test_keep_a_changelog_header() -> None:
    """Test that the changelog header follows Keep a Changelog format."""
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        import tomli as tomllib  # Fallback for Python <3.11

    cliff_config = Path(".cliff.toml")
    with cliff_config.open("rb") as f:
        config = tomllib.load(f)

    # Verify header contains Keep a Changelog reference
    header = config["changelog"]["header"]
    assert "Keep a Changelog" in header, "Expected header to reference Keep a Changelog"
    assert "Semantic Versioning" in header, "Expected header to reference Semantic Versioning"


def test_tag_pattern_configured() -> None:
    """Test that version tag pattern is configured correctly."""
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        import tomli as tomllib  # Fallback for Python <3.11

    cliff_config = Path(".cliff.toml")
    with cliff_config.open("rb") as f:
        config = tomllib.load(f)

    # Verify tag pattern matches project's versioning scheme (vX.Y.Z)
    tag_pattern = config["git"]["tag_pattern"]
    assert tag_pattern == "v[0-9]*", f"Expected tag_pattern to be 'v[0-9]*', got '{tag_pattern}'"


def test_changelog_body_template() -> None:
    """Test that the changelog body template is configured."""
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        import tomli as tomllib  # Fallback for Python <3.11

    cliff_config = Path(".cliff.toml")
    with cliff_config.open("rb") as f:
        config = tomllib.load(f)

    # Verify body template exists and contains version formatting
    body = config["changelog"]["body"]
    assert "{{ version" in body, "Expected body template to include version"
    assert "{{ timestamp" in body, "Expected body template to include timestamp"
    assert "{{ group" in body, "Expected body template to group commits"


def test_filter_unconventional_enabled() -> None:
    """Test that filtering of unconventional commits is enabled."""
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        import tomli as tomllib  # Fallback for Python <3.11

    cliff_config = Path(".cliff.toml")
    with cliff_config.open("rb") as f:
        config = tomllib.load(f)

    # Verify unconventional commits are filtered out
    assert (
        config["git"]["filter_unconventional"] is True
    ), "Expected filter_unconventional to be enabled"
