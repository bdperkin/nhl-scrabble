"""Unit tests for security module (log sanitization)."""

import logging

import pytest

from nhl_scrabble.security import SensitiveDataFilter, sanitize_for_logging


class TestSensitiveDataFilter:
    """Tests for SensitiveDataFilter class (PII protection)."""

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


class TestSanitizeForLogging:


    """Tests for sanitize_for_logging function (prevents log injection)."""

    def test_normal_text_unchanged(self) -> None:
        """Test that normal text without special characters is unchanged."""
        text = "normal text without special characters"
        result = sanitize_for_logging(text)
        assert result == text

    def test_unix_newline_escaped(self) -> None:
        """Test that Unix newlines (LF) are escaped."""
        text = "line1\nline2\nline3"
        result = sanitize_for_logging(text)
        assert result == "line1\\nline2\\nline3"
        assert "\n" not in result

    def test_windows_newline_escaped(self) -> None:
        """Test that Windows newlines (CRLF) are escaped."""
        text = "line1\r\nline2\r\nline3"
        result = sanitize_for_logging(text)
        assert result == "line1\\r\\nline2\\r\\nline3"
        assert "\r\n" not in result

    def test_mac_newline_escaped(self) -> None:
        """Test that Mac newlines (CR) are escaped."""
        text = "line1\rline2\rline3"
        result = sanitize_for_logging(text)
        assert result == "line1\\rline2\\rline3"
        assert "\r" not in result

    def test_tab_escaped(self) -> None:
        """Test that tabs are escaped."""
        text = "col1\tcol2\tcol3"
        result = sanitize_for_logging(text)
        assert result == "col1\\tcol2\\tcol3"
        assert "\t" not in result

    def test_control_characters_removed(self) -> None:
        """Test that control characters are removed."""
        # Include various control characters (0x00-0x1F, 0x7F)
        text = "text\x00with\x01control\x02chars\x7f"
        result = sanitize_for_logging(text)
        assert result == "textwithcontrolchars"
        # Verify no control characters remain
        for char in result:
            assert ord(char) >= 0x20
            assert ord(char) != 0x7F

    def test_integer_converted_to_string(self) -> None:
        """Test that integers are converted to strings."""
        value = 12345
        result = sanitize_for_logging(value)
        assert result == "12345"
        assert isinstance(result, str)

    def test_float_converted_to_string(self) -> None:
        """Test that floats are converted to strings."""
        value = 123.45
        result = sanitize_for_logging(value)
        assert result == "123.45"
        assert isinstance(result, str)

    def test_none_converted_to_string(self) -> None:
        """Test that None is converted to string 'None'."""
        value = None
        result = sanitize_for_logging(value)
        assert result == "None"
        assert isinstance(result, str)

    def test_exception_converted_and_sanitized(self) -> None:
        """Test that exceptions are converted to strings and sanitized."""
        exc = ValueError("Error message\nwith newline")
        result = sanitize_for_logging(exc)
        assert "Error message" in result
        assert "\n" not in result
        assert "\\n" in result

    def test_log_injection_attack_prevented(self) -> None:
        """Test that log injection attack is prevented."""
        # Attacker tries to inject fake log entry
        malicious_input = "valid input\n2024-01-01 ERROR Fake admin login from 192.168.1.1"
        result = sanitize_for_logging(malicious_input)

        # Newlines should be escaped, preventing log injection
        assert "\n" not in result
        assert "\\n" in result
        # The malicious log entry is visible but escaped
        assert result == "valid input\\n2024-01-01 ERROR Fake admin login from 192.168.1.1"

    def test_multiple_attack_vectors(self) -> None:
        """Test that multiple attack vectors are handled."""
        # Combination of newlines, tabs, control chars
        malicious = "user\nADMIN\ttrue\x00password=secret\rdeleted"
        result = sanitize_for_logging(malicious)

        # All dangerous characters should be escaped or removed
        assert "\n" not in result
        assert "\r" not in result
        assert "\t" not in result
        assert "\x00" not in result
        # Escaped versions should be present
        assert "\\n" in result
        assert "\\r" in result
        assert "\\t" in result

    def test_empty_string(self) -> None:
        """Test that empty string is handled."""
        result = sanitize_for_logging("")
        assert result == ""

    def test_url_with_newline_injection(self) -> None:
        """Test that URLs with newline injection are sanitized."""
        # Attacker tries to inject via URL parameter
        url = "https://api.example.com?user=admin\nX-Admin: true"
        result = sanitize_for_logging(url)

        assert "\n" not in result
        assert "\\n" in result
        assert result == "https://api.example.com?user=admin\\nX-Admin: true"

    def test_team_abbreviation_safe(self) -> None:
        """Test that normal team abbreviations work correctly."""
        team = "TOR"
        result = sanitize_for_logging(team)
        assert result == "TOR"

    def test_player_id_safe(self) -> None:
        """Test that normal player IDs work correctly."""
        player_id = 8478402
        result = sanitize_for_logging(player_id)
        assert result == "8478402"
