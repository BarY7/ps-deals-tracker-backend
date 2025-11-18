"""Base adapter interface for price sources."""

from abc import ABC, abstractmethod
from typing import Optional
from app.models import Game, Price


class PriceSourceAdapter(ABC):
    """
    Abstract base class for price source adapters.

    Each adapter should implement the get_price method to fetch
    current price data for a game from a specific source.
    """

    @abstractmethod
    async def get_price(self, game: Game) -> Optional[Price]:
        """
        Fetch current price for a game.

        Args:
            game: Game object to fetch price for

        Returns:
            Price object if successful, None if price unavailable
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the price source adapter."""
        pass
