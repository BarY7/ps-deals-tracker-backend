"""Game data model."""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class Game:
    """
    Represents a PlayStation game.

    Stored in the 'games' collection in Firestore.
    """

    id: str  # Slug/unique identifier
    title: str
    platform: str  # PS4, PS5, or both
    psn_id: Optional[str] = None
    release_date: Optional[str] = None  # ISO format date string
    genres: Optional[List[str]] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert game to dictionary for Firestore storage.

        Returns:
            Dict[str, Any]: Dictionary representation
        """
        data = asdict(self)
        # Convert datetime objects to Firestore timestamps
        if self.created_at:
            data["created_at"] = self.created_at
        if self.updated_at:
            data["updated_at"] = self.updated_at
        return {k: v for k, v in data.items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Game":
        """
        Create Game instance from Firestore dictionary.

        Args:
            data: Dictionary from Firestore

        Returns:
            Game: Game instance
        """
        # Handle datetime conversion
        if "created_at" in data and data["created_at"]:
            data["created_at"] = data["created_at"]
        if "updated_at" in data and data["updated_at"]:
            data["updated_at"] = data["updated_at"]

        return cls(**data)

    def __str__(self) -> str:
        """String representation of game."""
        return f"Game(id={self.id}, title={self.title}, platform={self.platform})"
