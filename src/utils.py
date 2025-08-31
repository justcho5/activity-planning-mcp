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
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD")

    if start_date > end_date:
        raise ValueError("Start date must be before end date")

    if start_date < datetime.now():
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
