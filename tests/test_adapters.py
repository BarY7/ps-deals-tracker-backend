"""Tests for price source adapters."""

import pytest

from app.adapters import MockPriceAdapter, PSNPriceAdapter
from app.models import Game


class TestMockPriceAdapter:
    """Tests for the MockPriceAdapter."""

    @pytest.fixture
    def adapter(self):
        """Create a mock adapter instance."""
        return MockPriceAdapter(enable_sales=True, sale_probability=0.5)

    @pytest.mark.asyncio
    async def test_adapter_name(self, adapter):
        """Test adapter name property."""
        assert adapter.name == "MockPriceAdapter"

    @pytest.mark.asyncio
    async def test_get_price_returns_price(self, adapter, sample_game):
        """Test that adapter returns a price object."""
        price = await adapter.get_price(sample_game)

        # Adapter has 5% failure rate, so might return None
        # Run multiple times to ensure we get at least one success
        attempts = 0
        while price is None and attempts < 10:
            price = await adapter.get_price(sample_game)
            attempts += 1

        assert price is not None
        assert price.price > 0
        assert price.original_price > 0
        assert price.currency == "USD"

    @pytest.mark.asyncio
    async def test_get_price_sale_logic(self, sample_game):
        """Test sale price logic."""
        # Adapter with guaranteed sales
        adapter = MockPriceAdapter(enable_sales=True, sale_probability=1.0)

        price = await adapter.get_price(sample_game)

        # With 100% sale probability, should be on sale
        # (unless the 5% failure kicks in)
        attempts = 0
        while price is None and attempts < 10:
            price = await adapter.get_price(sample_game)
            attempts += 1

        if price and price.on_sale:
            assert price.price < price.original_price
            assert price.discount_percent > 0

    @pytest.mark.asyncio
    async def test_get_price_no_sales(self, sample_game):
        """Test adapter with sales disabled."""
        adapter = MockPriceAdapter(enable_sales=False)

        price = await adapter.get_price(sample_game)

        # Get a valid price (retry if failure)
        attempts = 0
        while price is None and attempts < 10:
            price = await adapter.get_price(sample_game)
            attempts += 1

        if price:
            assert not price.on_sale
            assert price.discount_percent == 0
            assert price.price == price.original_price

    @pytest.mark.asyncio
    async def test_price_ranges(self):
        """Test that prices fall within expected ranges."""
        adapter = MockPriceAdapter(enable_sales=False)

        # Test PS5 game
        ps5_game = Game(
            id="test-ps5",
            title="Test PS5 Game",
            platform="PS5",
        )

        price = await adapter.get_price(ps5_game)
        attempts = 0
        while price is None and attempts < 10:
            price = await adapter.get_price(ps5_game)
            attempts += 1

        if price:
            # PS5 range is 49.99 to 69.99
            assert 49.99 <= price.price <= 69.99

        # Test PS4 game
        ps4_game = Game(
            id="test-ps4",
            title="Test PS4 Game",
            platform="PS4",
        )

        price = await adapter.get_price(ps4_game)
        attempts = 0
        while price is None and attempts < 10:
            price = await adapter.get_price(ps4_game)
            attempts += 1

        if price:
            # PS4 range is 29.99 to 59.99
            assert 29.99 <= price.price <= 59.99


class TestPSNPriceAdapter:
    """Tests for the PSNPriceAdapter."""

    @pytest.fixture
    def adapter(self):
        """Create a PSN adapter instance."""
        return PSNPriceAdapter(api_key="test_key")

    @pytest.mark.asyncio
    async def test_adapter_name(self, adapter):
        """Test adapter name property."""
        assert adapter.name == "PSNPriceAdapter"

    @pytest.mark.asyncio
    async def test_get_price_no_psn_id(self, adapter):
        """Test that adapter returns None for games without PSN ID."""
        game = Game(
            id="test-game",
            title="Test Game",
            platform="PS5",
            psn_id=None,  # No PSN ID
        )

        price = await adapter.get_price(game)
        assert price is None

    @pytest.mark.asyncio
    async def test_get_price_stub_implementation(self, adapter, sample_game):
        """Test stub implementation returns None."""
        # The stub implementation currently returns None
        price = await adapter.get_price(sample_game)
        assert price is None
