"""Position code to full name mapping utilities.

This module provides utilities for converting NHL position codes (C, L, R, D, G) to full position
names and position types (Forward, Defense, Goalie).
"""

# Position code to full position name mapping
POSITION_CODES = {
    "C": "Center",
    "L": "Left Wing",
    "R": "Right Wing",
    "D": "Defense",
    "G": "Goalie",
}

# Position code to position type mapping
POSITION_TYPES = {
    "C": "Forward",
    "L": "Forward",
    "R": "Forward",
    "D": "Defense",
    "G": "Goalie",
}


def get_position_name(position_code: str) -> str:
    """Convert position code to full position name.

    Args:
        position_code: Single-letter position code (C, L, R, D, G)

    Returns:
        Full position name (e.g., 'Center', 'Left Wing', 'Defense')
        Returns the original code if not recognized

    Examples:
        Get position names from codes:

        >>> get_position_name("C")
        'Center'
        >>> get_position_name("L")
        'Left Wing'
        >>> get_position_name("R")
        'Right Wing'
        >>> get_position_name("D")
        'Defense'
        >>> get_position_name("G")
        'Goalie'

        Case-insensitive matching:

        >>> get_position_name("c")
        'Center'
        >>> get_position_name("d")
        'Defense'

        Unknown codes return the code itself:

        >>> get_position_name("X")
        'X'
    """
    return POSITION_CODES.get(position_code.upper(), position_code)


def get_position_type(position_code: str) -> str:
    """Convert position code to position type.

    Args:
        position_code: Single-letter position code (C, L, R, D, G)

    Returns:
        Position type: 'Forward', 'Defense', or 'Goalie'
        Returns 'Unknown' if position code is not recognized

    Examples:
        Get position types from codes:

        >>> get_position_type("C")
        'Forward'
        >>> get_position_type("L")
        'Forward'
        >>> get_position_type("R")
        'Forward'
        >>> get_position_type("D")
        'Defense'
        >>> get_position_type("G")
        'Goalie'

        Case-insensitive matching:

        >>> get_position_type("c")
        'Forward'
        >>> get_position_type("g")
        'Goalie'

        Unknown codes return 'Unknown':

        >>> get_position_type("X")
        'Unknown'
    """
    return POSITION_TYPES.get(position_code.upper(), "Unknown")


def validate_position_code(position_code: str) -> bool:
    """Validate that a position code is recognized.

    Args:
        position_code: Single-letter position code to validate

    Returns:
        True if the position code is valid (C, L, R, D, G)
        False otherwise

    Examples:
        Validate position codes:

        >>> validate_position_code("C")
        True
        >>> validate_position_code("G")
        True
        >>> validate_position_code("X")
        False

        Case-insensitive validation:

        >>> validate_position_code("c")
        True
        >>> validate_position_code("d")
        True
    """
    return position_code.upper() in POSITION_CODES


def get_all_position_codes() -> list[str]:
    """Get all valid NHL position codes.

    Returns:
        List of all valid position codes: ['C', 'L', 'R', 'D', 'G']

    Examples:
        Get all position codes:

        >>> codes = get_all_position_codes()
        >>> len(codes)
        5
        >>> 'C' in codes
        True
        >>> 'G' in codes
        True
    """
    return list(POSITION_CODES.keys())


def get_all_position_names() -> list[str]:
    """Get all valid NHL position names.

    Returns:
        List of all position names: ['Center', 'Left Wing', 'Right Wing', 'Defense', 'Goalie']

    Examples:
        Get all position names:

        >>> names = get_all_position_names()
        >>> len(names)
        5
        >>> 'Center' in names
        True
        >>> 'Goalie' in names
        True
    """
    return list(POSITION_CODES.values())


def get_all_position_types() -> list[str]:
    """Get all unique position types.

    Returns:
        List of unique position types: ['Forward', 'Defense', 'Goalie']

    Examples:
        Get all position types:

        >>> types = get_all_position_types()
        >>> len(types)
        3
        >>> 'Forward' in types
        True
        >>> 'Defense' in types
        True
        >>> 'Goalie' in types
        True
    """
    return list(set(POSITION_TYPES.values()))
