"""Price data model."""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class Price:
    """
    Represents a price entry for a game.

    Stored in the 'prices' subcollection under each game document.
    """

    price: float
    original_price: float
    discount_percent: int
    on_sale: bool
    last_checked_at: datetime
    currency: str = "USD"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert price to dictionary for Firestore storage.

        Returns:
            Dict[str, Any]: Dictionary representation
        """
        data = asdict(self)
        # Firestore will handle datetime automatically
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Price":
        """
        Create Price instance from Firestore dictionary.

        Args:
            data: Dictionary from Firestore

        Returns:
            Price: Price instance
        """
        return cls(**data)

    def __str__(self) -> str:
        """String representation of price."""
        discount_info = f" ({self.discount_percent}% off)" if self.on_sale else ""
        return f"Price(${self.price:.2f}{discount_info}, checked={self.last_checked_at})"

    def is_significant_drop(self, old_price: Optional[float], threshold_percent: float = 10.0) -> bool:
        """
        Check if this price represents a significant drop from the old price.

        Args:
            old_price: Previous price
            threshold_percent: Minimum percent drop to be considered significant

        Returns:
            bool: True if price drop is significant
        """
        if old_price is None or old_price <= 0:
            return False

        drop_percent = ((old_price - self.price) / old_price) * 100
        return drop_percent >= threshold_percent
