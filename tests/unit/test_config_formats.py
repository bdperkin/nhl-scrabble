"""Unit tests for Config output format validation."""

import pytest

from nhl_scrabble.config import Config


class TestConfigOutputFormats:
    """Tests for Config output format validation (CLI-Config consistency)."""

    def test_config_accepts_all_cli_format_options(self) -> None:
        """Test Config accepts all formats offered by CLI.

        This test ensures Config validation stays in sync with CLI --format choices.
        Prevents pydantic ValidationError crashes when users select CLI-advertised formats.

        Related to issue #366 - Output format validation mismatch between CLI and Config.
        """
        # All formats advertised in CLI --format option (src/nhl_scrabble/cli.py line 408)
        cli_formats = [
            "text",
            "json",
            "yaml",
            "xml",
            "html",
            "table",
            "markdown",
            "csv",
            "excel",
            "template",
        ]

        for fmt in cli_formats:
            # Each format should be accepted by Config without ValidationError
            config = Config(output_format=fmt)
            assert config.output_format == fmt.lower()

    def test_config_output_format_rejects_invalid(self) -> None:
        """Test invalid formats are rejected with clear error message."""
        with pytest.raises(ValueError, match=r"Invalid value.*Allowed values"):
            Config(output_format="invalid_format")

    def test_config_output_format_case_insensitive(self) -> None:
        """Test output format is case-insensitive."""
        # Test various case combinations
        test_cases = [
            ("MARKDOWN", "markdown"),
            ("Json", "json"),
            ("YaML", "yaml"),
            ("XML", "xml"),
            ("TaBLe", "table"),
        ]

        for input_format, expected in test_cases:
            config = Config(output_format=input_format)
            assert config.output_format == expected

    @pytest.mark.parametrize(
        "output_format",
        [
            "text",
            "json",
            "yaml",
            "xml",
            "html",
            "table",
            "markdown",
            "csv",
            "excel",
            "template",
        ],
    )
    def test_config_individual_format_validation(self, output_format: str) -> None:
        """Test each format individually is accepted."""
        config = Config(output_format=output_format)
        assert config.output_format == output_format

    def test_from_env_accepts_all_cli_formats(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Config.from_env() accepts all CLI formats."""
        cli_formats = [
            "text",
            "json",
            "yaml",
            "xml",
            "html",
            "table",
            "markdown",
            "csv",
            "excel",
            "template",
        ]

        for fmt in cli_formats:
            # Clear any previous value
            monkeypatch.delenv("NHL_SCRABBLE_OUTPUT_FORMAT", raising=False)
            monkeypatch.setenv("NHL_SCRABBLE_OUTPUT_FORMAT", fmt)

            config = Config.from_env()
            assert config.output_format == fmt.lower()
