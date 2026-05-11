"""Unit tests for country code mapping utilities."""

from nhl_scrabble.utils.countries import (
    COUNTRY_CODES,
    get_all_countries,
    get_country_name,
    is_valid_country_code,
)


class TestCountryCodes:
    """Test country code to name mapping."""

    def test_country_codes_dict_exists(self) -> None:
        """Test that COUNTRY_CODES dictionary is defined."""
        assert isinstance(COUNTRY_CODES, dict)
        assert len(COUNTRY_CODES) > 0

    def test_major_hockey_countries_present(self) -> None:
        """Test that major hockey countries are in the mapping."""
        major_countries = {"CAN", "USA", "SWE", "FIN", "RUS", "CZE"}
        for country in major_countries:
            assert country in COUNTRY_CODES

    def test_country_names_are_strings(self) -> None:
        """Test that all country names are strings."""
        for code, name in COUNTRY_CODES.items():
            assert isinstance(code, str)
            assert isinstance(name, str)
            assert len(code) == 3  # ISO 3166-1 alpha-3
            assert len(name) > 0


class TestGetCountryName:
    """Test get_country_name function."""

    def test_get_canada(self) -> None:
        """Test getting Canada's name."""
        assert get_country_name("CAN") == "Canada"

    def test_get_usa(self) -> None:
        """Test getting United States' name."""
        assert get_country_name("USA") == "United States"

    def test_get_sweden(self) -> None:
        """Test getting Sweden's name."""
        assert get_country_name("SWE") == "Sweden"

    def test_get_finland(self) -> None:
        """Test getting Finland's name."""
        assert get_country_name("FIN") == "Finland"

    def test_get_russia(self) -> None:
        """Test getting Russia's name."""
        assert get_country_name("RUS") == "Russia"

    def test_get_czech_republic(self) -> None:
        """Test getting Czech Republic's name."""
        assert get_country_name("CZE") == "Czech Republic"

    def test_unknown_country_code_returns_code(self) -> None:
        """Test that unknown country codes return the code itself."""
        assert get_country_name("XXX") == "XXX"
        assert get_country_name("ZZZ") == "ZZZ"

    def test_empty_string_returns_empty(self) -> None:
        """Test that empty string returns empty string."""
        assert get_country_name("") == ""


class TestGetAllCountries:
    """Test get_all_countries function."""

    def test_returns_list_of_tuples(self) -> None:
        """Test that function returns list of (code, name) tuples."""
        countries = get_all_countries()
        assert isinstance(countries, list)
        assert len(countries) > 0
        assert all(isinstance(item, tuple) for item in countries)
        assert all(len(item) == 2 for item in countries)

    def test_sorted_alphabetically_by_name(self) -> None:
        """Test that countries are sorted alphabetically by name."""
        countries = get_all_countries()
        names = [name for _, name in countries]
        assert names == sorted(names)

    def test_contains_major_countries(self) -> None:
        """Test that major hockey countries are in the list."""
        countries = get_all_countries()
        codes = {code for code, _ in countries}
        assert "CAN" in codes
        assert "USA" in codes
        assert "SWE" in codes


class TestIsValidCountryCode:
    """Test is_valid_country_code function."""

    def test_valid_codes_return_true(self) -> None:
        """Test that valid country codes return True."""
        assert is_valid_country_code("CAN") is True
        assert is_valid_country_code("USA") is True
        assert is_valid_country_code("SWE") is True
        assert is_valid_country_code("FIN") is True

    def test_invalid_codes_return_false(self) -> None:
        """Test that invalid country codes return False."""
        assert is_valid_country_code("XXX") is False
        assert is_valid_country_code("ZZZ") is False
        assert is_valid_country_code("") is False

    def test_lowercase_codes_return_false(self) -> None:
        """Test that lowercase codes return False (case-sensitive)."""
        assert is_valid_country_code("can") is False
        assert is_valid_country_code("usa") is False
