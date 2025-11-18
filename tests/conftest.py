"""Pytest configuration and fixtures."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock

from app.models import Game, Price, Watchlist, WatchlistItem


@pytest.fixture
def sample_game():
    """Create a sample game for testing."""
    return Game(
        id="god-of-war-ragnarok",
        title="God of War Ragnarök",
        platform="PS5",
        psn_id="PPSA04521",
        release_date="2022-11-09",
        genres=["Action", "Adventure"],
        image_url="https://example.com/image.png",
        description="Test game description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_price():
    """Create a sample price for testing."""
    return Price(
        price=59.99,
        original_price=69.99,
        discount_percent=14,
        on_sale=True,
        last_checked_at=datetime.utcnow(),
        currency="USD",
    )


@pytest.fixture
def sample_price_no_sale():
    """Create a sample price with no sale."""
    return Price(
        price=69.99,
        original_price=69.99,
        discount_percent=0,
        on_sale=False,
        last_checked_at=datetime.utcnow(),
        currency="USD",
    )


@pytest.fixture
def sample_watchlist():
    """Create a sample watchlist for testing."""
    return Watchlist(
        user_id="test_user_1",
        games=[
            WatchlistItem(
                game_id="god-of-war-ragnarok",
                desired_price=49.99,
                desired_discount_pct=30,
                created_at=datetime.utcnow(),
            ),
            WatchlistItem(
                game_id="spiderman-2",
                desired_price=59.99,
                created_at=datetime.utcnow(),
            ),
        ],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def mock_firestore_client():
    """Create a mock Firestore client."""
    mock_client = MagicMock()
    return mock_client
