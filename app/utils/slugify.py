"""Utility functions for creating URL-safe slugs."""

import re
import unicodedata


def slugify(text: str, max_length: int = 50) -> str:
    """
    Convert text to a URL-safe slug.

    Args:
        text: Text to convert
        max_length: Maximum length of slug

    Returns:
        str: URL-safe slug

    Examples:
        >>> slugify("God of War: Ragnarök")
        'god-of-war-ragnarok'
        >>> slugify("Marvel's Spider-Man 2")
        'marvels-spider-man-2'
    """
    # Convert to lowercase
    text = text.lower()

    # Remove accents and special characters
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")

    # Replace spaces and special chars with hyphens
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)

    # Remove leading/trailing hyphens
    text = text.strip("-")

    # Truncate to max length
    if len(text) > max_length:
        text = text[:max_length].rsplit("-", 1)[0]

    return text


def game_id_from_title(title: str) -> str:
    """
    Generate a game ID from its title.

    Args:
        title: Game title

    Returns:
        str: Game ID (slug)

    Examples:
        >>> game_id_from_title("The Last of Us Part II")
        'the-last-of-us-part-ii'
    """
    return slugify(title)
