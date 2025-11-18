"""Tests for data models."""

import pytest
from datetime import datetime

from app.models import Game, Price, Watchlist, WatchlistItem, Notification


class TestGame:
    """Tests for the Game model."""

    def test_game_creation(self, sample_game):
        """Test creating a game instance."""
        assert sample_game.id == "god-of-war-ragnarok"
        assert sample_game.title == "God of War Ragnarök"
        assert sample_game.platform == "PS5"

    def test_game_to_dict(self, sample_game):
        """Test converting game to dictionary."""
        game_dict = sample_game.to_dict()

        assert game_dict["id"] == sample_game.id
        assert game_dict["title"] == sample_game.title
        assert game_dict["platform"] == sample_game.platform
        assert "created_at" in game_dict

    def test_game_from_dict(self, sample_game):
        """Test creating game from dictionary."""
        game_dict = sample_game.to_dict()
        restored_game = Game.from_dict(game_dict)

        assert restored_game.id == sample_game.id
        assert restored_game.title == sample_game.title
        assert restored_game.platform == sample_game.platform

    def test_game_str(self, sample_game):
        """Test game string representation."""
        game_str = str(sample_game)
        assert "god-of-war-ragnarok" in game_str
        assert "God of War Ragnarök" in game_str
        assert "PS5" in game_str


class TestPrice:
    """Tests for the Price model."""

    def test_price_creation(self, sample_price):
        """Test creating a price instance."""
        assert sample_price.price == 59.99
        assert sample_price.original_price == 69.99
        assert sample_price.discount_percent == 14
        assert sample_price.on_sale is True

    def test_price_to_dict(self, sample_price):
        """Test converting price to dictionary."""
        price_dict = sample_price.to_dict()

        assert price_dict["price"] == 59.99
        assert price_dict["on_sale"] is True
        assert "last_checked_at" in price_dict

    def test_price_from_dict(self, sample_price):
        """Test creating price from dictionary."""
        price_dict = sample_price.to_dict()
        restored_price = Price.from_dict(price_dict)

        assert restored_price.price == sample_price.price
        assert restored_price.on_sale == sample_price.on_sale

    def test_is_significant_drop(self, sample_price):
        """Test detecting significant price drops."""
        # 59.99 vs 69.99 is ~14% drop, should be significant
        assert sample_price.is_significant_drop(69.99, threshold_percent=10.0)

        # Not significant if threshold is too high
        assert not sample_price.is_significant_drop(69.99, threshold_percent=20.0)

        # No drop if old price is lower
        assert not sample_price.is_significant_drop(50.00, threshold_percent=10.0)

    def test_is_significant_drop_no_old_price(self, sample_price):
        """Test significant drop with no old price."""
        assert not sample_price.is_significant_drop(None, threshold_percent=10.0)


class TestWatchlist:
    """Tests for the Watchlist model."""

    def test_watchlist_creation(self, sample_watchlist):
        """Test creating a watchlist instance."""
        assert sample_watchlist.user_id == "test_user_1"
        assert len(sample_watchlist.games) == 2

    def test_watchlist_to_dict(self, sample_watchlist):
        """Test converting watchlist to dictionary."""
        watchlist_dict = sample_watchlist.to_dict()

        assert watchlist_dict["user_id"] == "test_user_1"
        assert len(watchlist_dict["games"]) == 2
        assert watchlist_dict["games"][0]["game_id"] == "god-of-war-ragnarok"

    def test_watchlist_from_dict(self, sample_watchlist):
        """Test creating watchlist from dictionary."""
        watchlist_dict = sample_watchlist.to_dict()
        restored = Watchlist.from_dict(watchlist_dict)

        assert restored.user_id == sample_watchlist.user_id
        assert len(restored.games) == len(sample_watchlist.games)

    def test_get_item(self, sample_watchlist):
        """Test getting a specific watchlist item."""
        item = sample_watchlist.get_item("god-of-war-ragnarok")

        assert item is not None
        assert item.game_id == "god-of-war-ragnarok"
        assert item.desired_price == 49.99

    def test_get_item_not_found(self, sample_watchlist):
        """Test getting a non-existent item."""
        item = sample_watchlist.get_item("nonexistent-game")
        assert item is None


class TestWatchlistItem:
    """Tests for the WatchlistItem model."""

    def test_should_notify_price_match(self):
        """Test notification when price matches desired price."""
        item = WatchlistItem(
            game_id="test-game",
            desired_price=49.99,
            created_at=datetime.utcnow(),
        )

        # Should notify when price is at or below desired
        assert item.should_notify(current_price=49.99, discount_percent=0)
        assert item.should_notify(current_price=39.99, discount_percent=0)

        # Should not notify when price is above desired
        assert not item.should_notify(current_price=59.99, discount_percent=0)

    def test_should_notify_discount_match(self):
        """Test notification when discount matches desired discount."""
        item = WatchlistItem(
            game_id="test-game",
            desired_discount_pct=30,
            created_at=datetime.utcnow(),
        )

        # Should notify when discount is at or above desired
        assert item.should_notify(current_price=49.99, discount_percent=30)
        assert item.should_notify(current_price=39.99, discount_percent=50)

        # Should not notify when discount is below desired
        assert not item.should_notify(current_price=59.99, discount_percent=20)

    def test_should_notify_either_condition(self):
        """Test notification when either price or discount condition is met."""
        item = WatchlistItem(
            game_id="test-game",
            desired_price=49.99,
            desired_discount_pct=30,
            created_at=datetime.utcnow(),
        )

        # Should notify if price condition is met
        assert item.should_notify(current_price=49.99, discount_percent=10)

        # Should notify if discount condition is met
        assert item.should_notify(current_price=59.99, discount_percent=30)

        # Should notify if both conditions are met
        assert item.should_notify(current_price=49.99, discount_percent=30)

        # Should not notify if neither condition is met
        assert not item.should_notify(current_price=59.99, discount_percent=10)


class TestNotification:
    """Tests for the Notification model."""

    def test_notification_creation(self):
        """Test creating a notification instance."""
        notification = Notification(
            user_id="test_user",
            game_id="test-game",
            game_title="Test Game",
            old_price=69.99,
            new_price=49.99,
            discount_percent=28,
            timestamp=datetime.utcnow(),
            type="price_drop",
            read=False,
        )

        assert notification.user_id == "test_user"
        assert notification.game_id == "test-game"
        assert notification.old_price == 69.99
        assert notification.new_price == 49.99

    def test_notification_to_dict(self):
        """Test converting notification to dictionary."""
        notification = Notification(
            user_id="test_user",
            game_id="test-game",
            game_title="Test Game",
            old_price=69.99,
            new_price=49.99,
            discount_percent=28,
            timestamp=datetime.utcnow(),
            type="price_drop",
            read=False,
        )

        notif_dict = notification.to_dict()

        assert notif_dict["user_id"] == "test_user"
        assert notif_dict["new_price"] == 49.99
        assert notif_dict["read"] is False

    def test_notification_str(self):
        """Test notification string representation."""
        notification = Notification(
            user_id="test_user",
            game_id="test-game",
            game_title="Test Game",
            old_price=69.99,
            new_price=49.99,
            discount_percent=28,
            timestamp=datetime.utcnow(),
        )

        notif_str = str(notification)
        assert "test_user" in notif_str
        assert "Test Game" in notif_str
        assert "69.99" in notif_str
        assert "49.99" in notif_str
