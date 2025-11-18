"""Notification data model."""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class Notification:
    """
    Represents a price drop notification for a user.

    Stored in the 'notifications' collection in Firestore.
    """

    user_id: str
    game_id: str
    game_title: str
    old_price: Optional[float]
    new_price: float
    discount_percent: int
    timestamp: datetime
    type: str = "price_drop"
    read: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert notification to dictionary for Firestore storage.

        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Notification":
        """
        Create Notification instance from Firestore dictionary.

        Args:
            data: Dictionary from Firestore

        Returns:
            Notification: Notification instance
        """
        return cls(**data)

    def __str__(self) -> str:
        """String representation of notification."""
        if self.old_price:
            return (
                f"Notification(user={self.user_id}, game={self.game_title}, "
                f"${self.old_price:.2f} -> ${self.new_price:.2f}, {self.discount_percent}% off)"
            )
        else:
            return (
                f"Notification(user={self.user_id}, game={self.game_title}, "
                f"${self.new_price:.2f}, {self.discount_percent}% off)"
            )
