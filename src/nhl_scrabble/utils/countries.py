"""Country code to full name mapping for NHL player nationalities.

This module provides mapping between ISO 3166-1 alpha-3 country codes (as used by the NHL API) and
full country names for display and internationalization purposes.
"""

from operator import itemgetter

# Country codes based on NHL player birthplaces
# Using ISO 3166-1 alpha-3 format (CAN, USA, SWE, etc.)
COUNTRY_CODES: dict[str, str] = {
    # North America
    "CAN": "Canada",
    "USA": "United States",
    # Nordic Countries
    "SWE": "Sweden",
    "FIN": "Finland",
    "NOR": "Norway",
    "DNK": "Denmark",
    "ISL": "Iceland",
    # Eastern Europe
    "RUS": "Russia",
    "CZE": "Czech Republic",
    "SVK": "Slovakia",
    "LVA": "Latvia",
    "BLR": "Belarus",
    "UKR": "Ukraine",
    "EST": "Estonia",
    "LTU": "Lithuania",
    "KAZ": "Kazakhstan",
    # Central/Western Europe
    "DEU": "Germany",
    "AUT": "Austria",
    "CHE": "Switzerland",
    "FRA": "France",
    "GBR": "Great Britain",
    "ITA": "Italy",
    "NLD": "Netherlands",
    "BEL": "Belgium",
    "POL": "Poland",
    "HUN": "Hungary",
    "ROU": "Romania",
    "BGR": "Bulgaria",
    # Other European
    "SVN": "Slovenia",
    "HRV": "Croatia",
    "SRB": "Serbia",
    "BIH": "Bosnia and Herzegovina",
    # Asia/Pacific
    "JPN": "Japan",
    "CHN": "China",
    "KOR": "South Korea",
    "AUS": "Australia",
    "NZL": "New Zealand",
    # Other
    "BRA": "Brazil",
    "MEX": "Mexico",
    "VEN": "Venezuela",
    "ZAF": "South Africa",
    "TZA": "Tanzania",
    "NGA": "Nigeria",
}


def get_country_name(country_code: str) -> str:
    """Convert ISO 3166-1 alpha-3 country code to full name.

    Args:
        country_code: Three-letter country code (e.g., 'CAN', 'USA', 'SWE')

    Returns:
        Full country name in English. Returns the country code itself
        if the code is not found in the mapping (unknown country).

    Examples:
        >>> get_country_name("CAN")
        'Canada'
        >>> get_country_name("USA")
        'United States'
        >>> get_country_name("SWE")
        'Sweden'
        >>> get_country_name("XXX")  # Unknown code
        'XXX'
    """
    return COUNTRY_CODES.get(country_code, country_code)


def get_all_countries() -> list[tuple[str, str]]:
    """Get all country codes and names as sorted list.

    Returns:
        List of (code, name) tuples sorted alphabetically by name

    Examples:
        >>> countries = get_all_countries()
        >>> countries[0]  # First country alphabetically
        ('AUS', 'Australia')
        >>> len(countries) > 30  # Many countries represented
        True
    """
    return sorted(COUNTRY_CODES.items(), key=itemgetter(1))


def is_valid_country_code(country_code: str) -> bool:
    """Check if a country code is valid/known.

    Args:
        country_code: Three-letter country code to validate

    Returns:
        True if the country code is in the mapping, False otherwise

    Examples:
        >>> is_valid_country_code("CAN")
        True
        >>> is_valid_country_code("USA")
        True
        >>> is_valid_country_code("XXX")
        False
    """
    return country_code in COUNTRY_CODES
