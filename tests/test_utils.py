"""Tests for utility functions."""

import pytest

from app.utils import slugify, game_id_from_title


class TestSlugify:
    """Tests for the slugify function."""

    def test_basic_slugify(self):
        """Test basic text to slug conversion."""
        assert slugify("God of War") == "god-of-war"
        assert slugify("The Last of Us") == "the-last-of-us"

    def test_slugify_with_special_chars(self):
        """Test slugify with special characters."""
        assert slugify("God of War: Ragnarök") == "god-of-war-ragnarok"
        assert slugify("Marvel's Spider-Man 2") == "marvels-spider-man-2"
        assert slugify("Ratchet & Clank") == "ratchet-clank"

    def test_slugify_with_numbers(self):
        """Test slugify preserves numbers."""
        assert slugify("Spider-Man 2") == "spider-man-2"
        assert slugify("Uncharted 4") == "uncharted-4"

    def test_slugify_removes_extra_spaces(self):
        """Test that extra spaces are handled correctly."""
        assert slugify("God  of   War") == "god-of-war"
        assert slugify("  Spider-Man  ") == "spider-man"

    def test_slugify_max_length(self):
        """Test max length truncation."""
        long_title = "This is a very long game title that should be truncated"
        slug = slugify(long_title, max_length=20)

        assert len(slug) <= 20
        assert not slug.endswith("-")  # Should not end with hyphen

    def test_slugify_empty_string(self):
        """Test slugify with empty string."""
        assert slugify("") == ""

    def test_slugify_only_special_chars(self):
        """Test slugify with only special characters."""
        result = slugify("!!!")
        assert result == ""


class TestGameIdFromTitle:
    """Tests for the game_id_from_title function."""

    def test_game_id_generation(self):
        """Test generating game IDs from titles."""
        assert game_id_from_title("God of War Ragnarök") == "god-of-war-ragnarok"
        assert game_id_from_title("The Last of Us Part II") == "the-last-of-us-part-ii"
        assert game_id_from_title("Marvel's Spider-Man 2") == "marvels-spider-man-2"

    def test_game_id_consistency(self):
        """Test that same title always produces same ID."""
        title = "Horizon Forbidden West"
        id1 = game_id_from_title(title)
        id2 = game_id_from_title(title)

        assert id1 == id2
