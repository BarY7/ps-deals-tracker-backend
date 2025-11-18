"""Tests for the price polling service."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime

from app.services import PricePollingService
from app.adapters import MockPriceAdapter
from app.models import Game, Price, Watchlist, WatchlistItem


class TestPricePollingService:
    """Tests for the PricePollingService."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock Firestore database."""
        mock = MagicMock()
        return mock

    @pytest.fixture
    def service(self, mock_db):
        """Create a price polling service with mock adapter."""
        adapters = [MockPriceAdapter(enable_sales=True, sale_probability=0.5)]

        with patch("app.services.price_poller.get_firestore_client", return_value=mock_db):
            service = PricePollingService(adapters=adapters, batch_size=5)
            return service

    def test_service_initialization(self, service):
        """Test service initialization."""
        assert len(service.adapters) == 1
        assert service.batch_size == 5

    def test_should_notify_new_sale(self, service):
        """Test notification logic when game goes on sale."""
        current_price = Price(
            price=39.99,
            original_price=59.99,
            discount_percent=33,
            on_sale=True,
            last_checked_at=datetime.utcnow(),
        )

        previous_price = Price(
            price=59.99,
            original_price=59.99,
            discount_percent=0,
            on_sale=False,
            last_checked_at=datetime.utcnow(),
        )

        assert service._should_notify(current_price, previous_price)

    def test_should_notify_significant_drop(self, service):
        """Test notification logic for significant price drop."""
        current_price = Price(
            price=49.99,
            original_price=69.99,
            discount_percent=28,
            on_sale=True,
            last_checked_at=datetime.utcnow(),
        )

        previous_price = Price(
            price=69.99,
            original_price=69.99,
            discount_percent=0,
            on_sale=False,
            last_checked_at=datetime.utcnow(),
        )

        # 69.99 -> 49.99 is ~28% drop, should trigger notification
        assert service._should_notify(current_price, previous_price)

    def test_should_not_notify_small_change(self, service):
        """Test that small price changes don't trigger notifications."""
        current_price = Price(
            price=68.99,
            original_price=69.99,
            discount_percent=1,
            on_sale=False,
            last_checked_at=datetime.utcnow(),
        )

        previous_price = Price(
            price=69.99,
            original_price=69.99,
            discount_percent=0,
            on_sale=False,
            last_checked_at=datetime.utcnow(),
        )

        # Small drop, no sale, should not notify
        assert not service._should_notify(current_price, previous_price)

    def test_should_notify_no_previous_price(self, service):
        """Test notification logic with no previous price."""
        current_price = Price(
            price=39.99,
            original_price=59.99,
            discount_percent=33,
            on_sale=True,
            last_checked_at=datetime.utcnow(),
        )

        # Should notify if game is on sale, even without previous price
        assert service._should_notify(current_price, None)

    @pytest.mark.asyncio
    async def test_fetch_price_success(self, service, sample_game):
        """Test fetching price using adapters."""
        price = await service._fetch_price(sample_game)

        # MockAdapter has 5% failure rate, retry if needed
        attempts = 0
        while price is None and attempts < 10:
            price = await service._fetch_price(sample_game)
            attempts += 1

        assert price is not None
        assert isinstance(price, Price)

    @pytest.mark.asyncio
    async def test_fetch_price_adapter_fallback(self, mock_db, sample_game):
        """Test that service tries multiple adapters."""
        # Create an adapter that always fails
        failing_adapter = MagicMock()
        failing_adapter.name = "FailingAdapter"
        failing_adapter.get_price = AsyncMock(return_value=None)

        # Create a working adapter
        working_adapter = MockPriceAdapter()

        with patch("app.services.price_poller.get_firestore_client", return_value=mock_db):
            service = PricePollingService(
                adapters=[failing_adapter, working_adapter],
                batch_size=5,
            )

            price = await service._fetch_price(sample_game)

            # Should get price from working adapter after failing adapter fails
            attempts = 0
            while price is None and attempts < 10:
                price = await service._fetch_price(sample_game)
                attempts += 1

            # Should have tried the failing adapter
            assert failing_adapter.get_price.called


class TestWatchlistNotifications:
    """Tests for watchlist-based notifications."""

    @pytest.fixture
    def service(self):
        """Create service for testing."""
        mock_db = MagicMock()
        adapters = [MockPriceAdapter()]

        with patch("app.services.price_poller.get_firestore_client", return_value=mock_db):
            service = PricePollingService(adapters=adapters)
            return service

    def test_fetch_all_watchlists_error_handling(self, service):
        """Test error handling when fetching watchlists."""
        # Mock the collection to raise an error
        service.db.collection.side_effect = Exception("Database error")

        watchlists = service._fetch_all_watchlists()

        # Should return empty list on error
        assert watchlists == []
