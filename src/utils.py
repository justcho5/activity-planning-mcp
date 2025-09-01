from typing import List
from datetime import datetime


def validate_location(location: str) -> str:

    location = location.strip()

    if not location:
        raise ValueError("Location is required")

    if len(location) < 2:
        raise ValueError("Location must be at least 2 characters long")

    if len(location) > 200:
        raise ValueError("Location is too long")

    invalid_chars = get_invalid_chars()

    if any(char in location for char in invalid_chars):
        raise ValueError("Location contains invalid characters")

    return location


def validate_keyword(keyword: str) -> str:

    keyword = keyword.strip()

    if len(keyword) > 200:
        raise ValueError("Keyword is too long")

    invalid_chars = get_invalid_chars()

    if any(char in keyword for char in invalid_chars):
        raise ValueError("Keyword contains invalid characters")

    return keyword


def validate_start_end_dates(start_date: str, end_date: str):

    try:
        sd = datetime.strptime(start_date, "%Y-%m-%d")
        ed = datetime.strptime(end_date, "%Y-%m-%d")

    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD")

    if sd >= ed:
        raise ValueError("Start date must be before end date")

    if sd <= datetime.now():
        raise ValueError("Start date must be in the future")

    return start_date, end_date


def get_invalid_chars() -> List[str]:
    return [
        "<",
        ">",
        ":",
        "/",
        "\\",
        "|",
        "?",
        "*",
        "{",
        "}",
        "(",
        ")",
        "[",
        "]",
        "@",
        "%",
        "&",
        "$",
        "#",
        "^",
        "=",
        "+",
        "`",
    ]


def format_coordinates(lat: float, lon: float) -> str:
    """
    Format coordinates as a string for APIs that expect "lat,lon" format.

    Args:
        lat: Latitude
        lon: Longitude

    Returns:
        Formatted string "latitude,longitude"
    """
    return f"{lat},{lon}"


def is_coordinates(location: str) -> bool:
    """
    Check if a location string is already in coordinate format.

    Args:
        location: Location string to check

    Returns:
        True if location is coordinates ("lat,lon"), False otherwise
    """
    try:
        parts = location.split(",")
        if len(parts) != 2:
            return False

        lat = float(parts[0].strip())
        lng = float(parts[1].strip())

        # Check valid coordinate ranges
        return -90 <= lat <= 90 and -180 <= lng <= 180

    except (ValueError, AttributeError):
        return False
