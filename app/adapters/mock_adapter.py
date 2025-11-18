"""Mock price adapter for local testing and development."""

import random
from datetime import datetime
from typing import Optional

from app.adapters.base_adapter import PriceSourceAdapter
from app.models import Game, Price


class MockPriceAdapter(PriceSourceAdapter):
    """
    Mock price adapter that generates realistic test data.

    Useful for local development and testing without hitting real APIs.
    """

    def __init__(self, enable_sales: bool = True, sale_probability: float = 0.3):
        """
        Initialize mock adapter.

        Args:
            enable_sales: Whether to randomly generate sales
            sale_probability: Probability (0.0-1.0) that a game is on sale
        """
        self.enable_sales = enable_sales
        self.sale_probability = sale_probability

        # Predefined price ranges based on game platform
        self.price_ranges = {
            "PS5": (49.99, 69.99),
            "PS4": (29.99, 59.99),
            "PS4/PS5": (39.99, 69.99),
        }

    @property
    def name(self) -> str:
        """Name of the adapter."""
        return "MockPriceAdapter"

    async def get_price(self, game: Game) -> Optional[Price]:
        """
        Generate mock price data for a game.

        Args:
            game: Game object

        Returns:
            Price object with mock data
        """
        # Simulate occasional API failures
        if random.random() < 0.05:  # 5% failure rate
            return None

        # Get price range for platform
        price_range = self.price_ranges.get(game.platform, (19.99, 59.99))
        original_price = round(random.uniform(*price_range), 2)

        # Determine if on sale
        on_sale = self.enable_sales and random.random() < self.sale_probability

        if on_sale:
            # Generate discount between 10% and 75%
            discount_percent = random.choice([10, 15, 20, 25, 30, 40, 50, 60, 75])
            current_price = round(original_price * (1 - discount_percent / 100), 2)
        else:
            discount_percent = 0
            current_price = original_price

        return Price(
            price=current_price,
            original_price=original_price,
            discount_percent=discount_percent,
            on_sale=on_sale,
            last_checked_at=datetime.utcnow(),
            currency="USD",
        )
