"""Watchlist data model."""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class WatchlistItem:
    """Represents a single item in a user's watchlist."""

    game_id: str
    desired_price: Optional[float] = None
    desired_discount_pct: Optional[int] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WatchlistItem":
        """Create instance from dictionary."""
        return cls(**data)

    def should_notify(self, current_price: float, discount_percent: int) -> bool:
        """
        Check if this watchlist item should trigger a notification.

        Args:
            current_price: Current price of the game
            discount_percent: Current discount percentage

        Returns:
            bool: True if notification should be sent
        """
        if self.desired_price and current_price <= self.desired_price:
            return True

        if self.desired_discount_pct and discount_percent >= self.desired_discount_pct:
            return True

        return False


@dataclass
class Watchlist:
    """
    Represents a user's watchlist.

    Stored in the 'watchlists' collection in Firestore.
    """

    user_id: str
    games: List[WatchlistItem]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore storage."""
        return {
            "user_id": self.user_id,
            "games": [item.to_dict() for item in self.games],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Watchlist":
        """Create instance from Firestore dictionary."""
        games_data = data.get("games", [])
        games = [WatchlistItem.from_dict(item) for item in games_data]

        return cls(
            user_id=data["user_id"],
            games=games,
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def get_item(self, game_id: str) -> Optional[WatchlistItem]:
        """Get watchlist item for a specific game."""
        for item in self.games:
            if item.game_id == game_id:
                return item
        return None
