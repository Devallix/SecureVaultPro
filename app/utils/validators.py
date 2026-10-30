"""Input validation utilities for SecureVault Pro."""

from app.utils.constants import EMAIL_PATTERN, URL_PATTERN


def validate_email(email: str) -> bool:
    """Validate an email address format.

    Args:
        email: The email address to validate.

    Returns:
        True if the email format is valid.
    """
    return bool(EMAIL_PATTERN.match(email))


def validate_url(url: str) -> bool:
    """Validate a URL format.

    Args:
        url: The URL to validate.

    Returns:
        True if the URL format is valid.
    """
    return bool(URL_PATTERN.match(url))


def validate_password_length(length: int, min_len: int = 8, max_len: int = 128) -> bool:
    """Validate password length constraints.

    Args:
        length: Password length to check.
        min_len: Minimum allowed length.
        max_len: Maximum allowed length.

    Returns:
        True if the length is within bounds.
    """
    return min_len <= length <= max_len


def sanitize_filename(filename: str) -> str:
    """Remove or replace characters unsafe for filenames.

    Args:
        filename: The raw filename.

    Returns:
        Sanitized filename safe for all platforms.
    """
    unsafe_chars = '<>:"/\\|?*'
    result = filename
    for char in unsafe_chars:
        result = result.replace(char, "_")
    return result.strip(". ")
