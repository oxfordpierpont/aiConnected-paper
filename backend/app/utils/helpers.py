"""Miscellaneous helper functions."""

import re
from datetime import datetime, timedelta
from typing import Optional


def generate_slug(text: str) -> str:
    """Generate a URL-safe slug from text."""
    from slugify import slugify
    return slugify(text, lowercase=True, max_length=100)


def calculate_expiry_date(days: int = 1095) -> datetime:
    """Calculate document expiry date (default 3 years)."""
    return datetime.utcnow() + timedelta(days=days)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for safe storage."""
    # Remove path separators and special characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    # Limit length
    return sanitized[:255]


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
