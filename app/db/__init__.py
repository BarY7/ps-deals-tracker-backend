"""Database initialization and helpers."""

from app.db.firestore import (
    get_firestore_client,
    get_async_firestore_client,
    close_clients,
    GAMES_COLLECTION,
    PRICES_SUBCOLLECTION,
    WATCHLISTS_COLLECTION,
    NOTIFICATIONS_COLLECTION,
)

__all__ = [
    "get_firestore_client",
    "get_async_firestore_client",
    "close_clients",
    "GAMES_COLLECTION",
    "PRICES_SUBCOLLECTION",
    "WATCHLISTS_COLLECTION",
    "NOTIFICATIONS_COLLECTION",
]
