"""Unit tests for security module (log sanitization)."""

import logging

import pytest

from nhl_scrabble.security import SensitiveDataFilter


class TestSensitiveDataFilter:
    """Tests for SensitiveDataFilter class."""

    def test_sanitize_api_key_in_url(self) -> None:
        """Test that API keys in URLs are sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Making request to https://api.example.com?api_key=secret123",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "secret123" not in record.msg
        assert "api_key=***" in record.msg

    def test_sanitize_api_key_case_insensitive(self) -> None:
        """Test that API key sanitization is case-insensitive."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Request: https://api.example.com?API_KEY=secret123",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "secret123" not in record.msg
        assert "API_KEY=***" in record.msg

    def test_sanitize_apikey_no_underscore(self) -> None:
        """Test that apikey (without underscore) is sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="URL: https://api.example.com?apikey=secret123",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "secret123" not in record.msg
        assert "apikey=***" in record.msg

    def test_sanitize_generic_key(self) -> None:
        """Test that generic key= parameter is sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Request: https://api.example.com?key=secret123",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "secret123" not in record.msg
        assert "key=***" in record.msg

    def test_sanitize_bearer_token(self) -> None:
        """Test that Bearer tokens are sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Headers: Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in record.msg
        assert "Bearer ***" in record.msg

    def test_sanitize_bearer_without_authorization(self) -> None:
        """Test that standalone Bearer token is sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Token: Bearer sk-1234567890abcdef",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "sk-1234567890abcdef" not in record.msg
        assert "Bearer ***" in record.msg

    def test_sanitize_basic_auth(self) -> None:
        """Test that Basic auth tokens are sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Headers: Authorization: Basic dXNlcjpwYXNz",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "dXNlcjpwYXNz" not in record.msg
        assert "Basic ***" in record.msg

    def test_sanitize_password_in_url(self) -> None:
        """Test that passwords in URLs are sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Connecting to https://user:MyP@ssw0rd@api.example.com",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "MyP@ssw0rd" not in record.msg
        assert "user:***@api.example.com" in record.msg

    def test_sanitize_secret_parameter(self) -> None:
        """Test that secret= parameter is sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="URL: https://api.example.com?secret=mysecretvalue",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "mysecretvalue" not in record.msg
        assert "secret=***" in record.msg

    def test_sanitize_token_parameter(self) -> None:
        """Test that token= parameter is sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Request: https://api.example.com?token=abc123xyz",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "abc123xyz" not in record.msg
        assert "token=***" in record.msg

    def test_sanitize_environment_variable_api_key(self) -> None:
        """Test that environment variables with API_KEY are sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Config error: NHL_SCRABBLE_API_KEY=sk-1234567890abcdef",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "sk-1234567890abcdef" not in record.msg
        assert "NHL_SCRABBLE_API_KEY=***" in record.msg

    def test_sanitize_environment_variable_token(self) -> None:
        """Test that environment variables with TOKEN are sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Error: NHL_SCRABBLE_AUTH_TOKEN = mytoken123",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "mytoken123" not in record.msg
        assert "NHL_SCRABBLE_AUTH_TOKEN = ***" in record.msg

    def test_sanitize_environment_variable_secret(self) -> None:
        """Test that environment variables with SECRET are sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="NHL_SCRABBLE_CLIENT_SECRET=very-secret-value",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "very-secret-value" not in record.msg
        assert "NHL_SCRABBLE_CLIENT_SECRET=***" in record.msg

    def test_sanitize_environment_variable_password(self) -> None:
        """Test that environment variables with PASSWORD are sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="NHL_SCRABBLE_DB_PASSWORD = P@ssw0rd!",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "P@ssw0rd!" not in record.msg
        assert "NHL_SCRABBLE_DB_PASSWORD = ***" in record.msg

    def test_sanitize_with_args(self) -> None:
        """Test that args in format strings are sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Request to %s failed",
            args=("https://api.example.com?token=secret123",),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert isinstance(record.args, tuple)  # Type narrowing for mypy
        assert isinstance(record.args[0], str)  # Type narrowing for indexed access
        assert "secret123" not in record.args[0]
        assert "token=***" in record.args[0]

    def test_sanitize_multiple_args(self) -> None:
        """Test that multiple args are sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Request %s returned %s",
            args=(
                "https://api.example.com?api_key=secret1",
                "Authorization: Bearer token123",
            ),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert isinstance(record.args, tuple)  # Type narrowing for mypy
        assert isinstance(record.args[0], str)  # Type narrowing for indexed access
        assert isinstance(record.args[1], str)  # Type narrowing for indexed access
        assert "secret1" not in record.args[0]
        assert "api_key=***" in record.args[0]
        assert "token123" not in record.args[1]
        assert "Bearer ***" in record.args[1]

    def test_non_string_args_not_affected(self) -> None:
        """Test that non-string args are not modified."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Processed %d items in %f seconds",
            args=(42, 1.5),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert record.args == (42, 1.5)

    def test_mixed_args_types(self) -> None:
        """Test that mixed arg types are handled correctly."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Request %s took %d ms with status %s",
            args=("https://api.example.com?key=secret", 150, "200 OK"),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert isinstance(record.args, tuple)  # Type narrowing for mypy
        assert isinstance(record.args[0], str)  # Type narrowing for indexed access
        assert "secret" not in record.args[0]
        assert "key=***" in record.args[0]
        assert record.args[1] == 150
        assert record.args[2] == "200 OK"

    def test_non_string_message_not_affected(self) -> None:
        """Test that non-string messages are not modified."""
        filter_instance = SensitiveDataFilter()

        # Create record with non-string message
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg={"key": "value"},
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        # Should not crash and message should be unchanged
        assert record.msg == {"key": "value"}

    def test_multiple_patterns_in_same_message(self) -> None:
        """Test that multiple sensitive patterns in same message are all sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Request https://api.example.com?api_key=key1&token=tok1 with Bearer jwt123",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "key1" not in record.msg
        assert "tok1" not in record.msg
        assert "jwt123" not in record.msg
        assert "api_key=***" in record.msg
        assert "token=***" in record.msg
        assert "Bearer ***" in record.msg

    def test_filter_always_returns_true(self) -> None:
        """Test that filter always returns True (allows logging)."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Any message",
            args=(),
            exc_info=None,
        )

        result = filter_instance.filter(record)

        assert result is True

    def test_integration_with_logger(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that filter works with actual logger."""
        logger = logging.getLogger("test_security_integration")
        logger.handlers.clear()

        handler = logging.StreamHandler()
        handler.addFilter(SensitiveDataFilter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        with caplog.at_level(logging.INFO, logger="test_security_integration"):
            logger.info("API request: https://api.example.com?api_key=secret123")

        assert "secret123" not in caplog.text
        assert "api_key=***" in caplog.text

        # Clean up
        logger.handlers.clear()

    def test_url_with_ampersand_separator(self) -> None:
        """Test sanitization with ampersand parameter separator."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="URL: https://api.example.com?foo=bar&api_key=secret&baz=qux",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "secret" not in record.msg
        assert "api_key=***" in record.msg
        assert "foo=bar" in record.msg  # Other params preserved
        assert "baz=qux" in record.msg

    def test_preserves_non_sensitive_data(self) -> None:
        """Test that non-sensitive data is preserved."""
        filter_instance = SensitiveDataFilter()

        original_msg = (
            "Processing NHL team data from https://api.example.com/teams "
            "with 32 teams and status: success"
        )

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=original_msg,
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        # Non-sensitive message should be unchanged
        assert record.msg == original_msg

    # PII Protection Tests

    def test_sanitize_player_name_in_player_score_repr(self) -> None:
        """Test that player names in PlayerScore repr are sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Processing PlayerScore(name='Connor McDavid', score=42, team='EDM')",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "Connor McDavid" not in record.msg
        assert "[REDACTED-NAME]" in record.msg
        assert "score=42" in record.msg  # Non-PII preserved
        assert "team='EDM'" in record.msg  # Non-PII preserved

    def test_sanitize_player_name_with_colon(self) -> None:
        """Test that player names after 'player:' are sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Processing player: Connor McDavid",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "Connor McDavid" not in record.msg
        assert "[REDACTED-NAME]" in record.msg

    def test_sanitize_player_name_with_quotes(self) -> None:
        """Test that quoted player names are sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Player name: 'Auston Matthews'",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "Auston Matthews" not in record.msg
        assert "[REDACTED-NAME]" in record.msg

    def test_sanitize_first_name_field(self) -> None:
        """Test that firstName field values are sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Player data: firstName: Connor, position: C",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "Connor" not in record.msg
        assert "[REDACTED]" in record.msg
        assert "position: C" in record.msg  # Non-PII preserved

    def test_sanitize_last_name_field(self) -> None:
        """Test that lastName field values are sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="lastName='McDavid'",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "McDavid" not in record.msg
        assert "[REDACTED]" in record.msg

    def test_sanitize_email_address(self) -> None:
        """Test that email addresses are sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Contact: player@example.com for more info",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "player@example.com" not in record.msg
        assert "[REDACTED-EMAIL]" in record.msg

    def test_sanitize_birthdate_iso_format(self) -> None:
        """Test that birthdates in ISO format (YYYY-MM-DD) are sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Player info: birthDate: 1997-01-13",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "1997-01-13" not in record.msg
        assert "[REDACTED-DATE]" in record.msg

    def test_sanitize_birthdate_slash_format(self) -> None:
        """Test that birthdates with slashes (YYYY/MM/DD) are sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="birthdate=1997/01/13",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "1997/01/13" not in record.msg
        assert "[REDACTED-DATE]" in record.msg

    def test_sanitize_birthdate_us_format(self) -> None:
        """Test that birthdates in US format (MM/DD/YYYY) are sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="birth_date='01/13/1997'",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "01/13/1997" not in record.msg
        assert "[REDACTED-DATE]" in record.msg

    def test_sanitize_birthplace(self) -> None:
        """Test that birthplace information is sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="birthplace: Toronto, ON, Canada",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "Toronto, ON, Canada" not in record.msg
        assert "[REDACTED-PLACE]" in record.msg

    def test_sanitize_birthcity(self) -> None:
        """Test that birthCity field is sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Player from birthCity='Montreal'",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "Montreal" not in record.msg
        assert "[REDACTED-PLACE]" in record.msg

    def test_sanitize_multiple_pii_in_one_message(self) -> None:
        """Test that multiple PII elements in one message are all sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Player: Connor McDavid, birthdate: 1997-01-13, email: player@example.com",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "Connor McDavid" not in record.msg
        assert "1997-01-13" not in record.msg
        assert "player@example.com" not in record.msg
        assert "[REDACTED-NAME]" in record.msg
        assert "[REDACTED-DATE]" in record.msg
        assert "[REDACTED-EMAIL]" in record.msg

    def test_sanitize_hyphenated_names(self) -> None:
        """Test that hyphenated player names are sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Processing player: Marc-Andre Fleury",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "Marc-Andre Fleury" not in record.msg
        assert "[REDACTED-NAME]" in record.msg

    def test_preserves_team_abbreviations(self) -> None:
        """Test that team abbreviations are not sanitized as names."""
        filter_instance = SensitiveDataFilter()

        original_msg = "Teams: TOR, MTL, EDM playing tonight"

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=original_msg,
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        # Team abbreviations should not be redacted
        assert record.msg == original_msg

    def test_preserves_division_names(self) -> None:
        """Test that division/conference names are not sanitized."""
        filter_instance = SensitiveDataFilter()

        original_msg = "Atlantic Division standings"

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=original_msg,
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        # Division names should not be redacted (not in PII context)
        assert record.msg == original_msg

    def test_pii_sanitization_with_args(self) -> None:
        """Test that PII in args is sanitized."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Processing player: %s",
            args=("Connor McDavid",),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert isinstance(record.args, tuple)
        assert isinstance(record.args[0], str)
        assert "Connor McDavid" not in record.args[0]
        assert "[REDACTED-NAME]" in record.args[0]

    def test_combined_credentials_and_pii(self) -> None:
        """Test that both credentials and PII are sanitized together."""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="API call with api_key=secret123 for player: Sidney Crosby",
            args=(),
            exc_info=None,
        )

        filter_instance.filter(record)

        assert "secret123" not in record.msg
        assert "Sidney Crosby" not in record.msg
        assert "api_key=***" in record.msg
        assert "[REDACTED-NAME]" in record.msg
