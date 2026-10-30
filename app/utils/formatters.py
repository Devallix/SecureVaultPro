"""Display formatting utilities for SecureVault Pro."""

from datetime import datetime


def format_file_size(size_bytes: int) -> str:
    """Format bytes into human-readable file size.

    Args:
        size_bytes: Size in bytes.

    Returns:
        Formatted string like '1.5 MB'.
    """
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    if unit_index == 0:
        return f"{int(size)} B"
    return f"{size:.1f} {units[unit_index]}"


def format_datetime(dt: datetime | None) -> str:
    """Format a datetime for display.

    Args:
        dt: The datetime to format, or None.

    Returns:
        Formatted datetime string, or empty string if None.
    """
    if dt is None:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_relative_time(dt: datetime | None) -> str:
    """Format a datetime as relative time (e.g., '2 hours ago').

    Args:
        dt: The datetime to format.

    Returns:
        Relative time string.
    """
    if dt is None:
        return "Never"
    now = datetime.now()
    diff = now - dt
    seconds = int(diff.total_seconds())
    if seconds < 60:
        return "Just now"
    if seconds < 3600:
        minutes = seconds // 60
        label = "minute" if minutes == 1 else "minutes"
        return f"{minutes} {label} ago"
    if seconds < 86400:
        hours = seconds // 3600
        label = "hour" if hours == 1 else "hours"
        return f"{hours} {label} ago"
    days = seconds // 86400
    if days < 30:
        label = "day" if days == 1 else "days"
        return f"{days} {label} ago"
    months = days // 30
    label = "month" if months == 1 else "months"
    return f"{months} {label} ago"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format a float as a percentage string.

    Args:
        value: Float value (0.0 to 1.0).
        decimals: Number of decimal places.

    Returns:
        Formatted percentage string.
    """
    return f"{value * 100:.{decimals}f}%"
