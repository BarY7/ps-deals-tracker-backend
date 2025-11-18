"""Firestore database initialization and helper functions."""

import os
from typing import Optional
from google.cloud import firestore
from google.cloud.firestore_v1 import AsyncClient


# Global client instances
_db_client: Optional[firestore.Client] = None
_async_db_client: Optional[AsyncClient] = None


def get_firestore_client() -> firestore.Client:
    """
    Get or create a Firestore client instance.

    For local development, set FIRESTORE_EMULATOR_HOST environment variable.
    Example: export FIRESTORE_EMULATOR_HOST=localhost:8080

    Returns:
        firestore.Client: Firestore client instance
    """
    global _db_client

    if _db_client is None:
        project_id = os.getenv("GCP_PROJECT", "ps-deals-tracker")

        if os.getenv("FIRESTORE_EMULATOR_HOST"):
            print(f"[Firestore] Using emulator at {os.getenv('FIRESTORE_EMULATOR_HOST')}")
            _db_client = firestore.Client(project=project_id)
        else:
            print(f"[Firestore] Connecting to production Firestore for project: {project_id}")
            _db_client = firestore.Client(project=project_id)

    return _db_client


def get_async_firestore_client() -> AsyncClient:
    """
    Get or create an async Firestore client instance.

    Returns:
        AsyncClient: Async Firestore client instance
    """
    global _async_db_client

    if _async_db_client is None:
        project_id = os.getenv("GCP_PROJECT", "ps-deals-tracker")

        if os.getenv("FIRESTORE_EMULATOR_HOST"):
            print(f"[Firestore] Using emulator at {os.getenv('FIRESTORE_EMULATOR_HOST')}")
            _async_db_client = AsyncClient(project=project_id)
        else:
            print(f"[Firestore] Connecting to production Firestore for project: {project_id}")
            _async_db_client = AsyncClient(project=project_id)

    return _async_db_client


def close_clients():
    """Close all Firestore client connections."""
    global _db_client, _async_db_client

    if _db_client:
        _db_client.close()
        _db_client = None

    if _async_db_client:
        _async_db_client.close()
        _async_db_client = None


# Collection names
GAMES_COLLECTION = "games"
PRICES_SUBCOLLECTION = "prices"
WATCHLISTS_COLLECTION = "watchlists"
NOTIFICATIONS_COLLECTION = "notifications"
