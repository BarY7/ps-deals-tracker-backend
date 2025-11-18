"""Price polling service for fetching and updating game prices."""

import asyncio
from datetime import datetime
from typing import List, Optional
from google.cloud import firestore

from app.adapters import PriceSourceAdapter
from app.models import Game, Price, Notification, Watchlist, WatchlistItem
from app.db import (
    get_firestore_client,
    GAMES_COLLECTION,
    PRICES_SUBCOLLECTION,
    WATCHLISTS_COLLECTION,
    NOTIFICATIONS_COLLECTION,
)


class PricePollingService:
    """
    Service for polling game prices and creating notifications.

    This service:
    1. Fetches current prices for all games using configured adapters
    2. Saves price data to Firestore
    3. Compares with previous prices
    4. Checks user watchlists
    5. Creates notifications for price drops
    """

    def __init__(self, adapters: List[PriceSourceAdapter], batch_size: int = 10):
        """
        Initialize the price polling service.

        Args:
            adapters: List of price source adapters to try in order
            batch_size: Number of games to process concurrently
        """
        self.adapters = adapters
        self.batch_size = batch_size
        self.db = get_firestore_client()

    async def poll_all_games(self) -> dict:
        """
        Poll prices for all games in the database.

        Returns:
            dict: Statistics about the polling run
        """
        print("[Price Poller] Starting price polling run...")
        start_time = datetime.utcnow()

        # Fetch all games from Firestore
        games = self._fetch_all_games()
        print(f"[Price Poller] Found {len(games)} games to process")

        # Process games in batches
        stats = {
            "total_games": len(games),
            "successful": 0,
            "failed": 0,
            "notifications_created": 0,
        }

        for i in range(0, len(games), self.batch_size):
            batch = games[i : i + self.batch_size]
            batch_results = await asyncio.gather(
                *[self._process_game(game) for game in batch],
                return_exceptions=True,
            )

            for result in batch_results:
                if isinstance(result, Exception):
                    print(f"[Price Poller] Error processing game: {result}")
                    stats["failed"] += 1
                elif result:
                    stats["successful"] += 1
                    stats["notifications_created"] += result.get("notifications", 0)
                else:
                    stats["failed"] += 1

        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        print(f"[Price Poller] Polling complete in {duration:.2f}s")
        print(f"[Price Poller] Stats: {stats}")

        return stats

    def _fetch_all_games(self) -> List[Game]:
        """
        Fetch all games from Firestore.

        Returns:
            List[Game]: List of all games
        """
        games_ref = self.db.collection(GAMES_COLLECTION)
        docs = games_ref.stream()

        games = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            games.append(Game.from_dict(data))

        return games

    async def _process_game(self, game: Game) -> Optional[dict]:
        """
        Process a single game: fetch price, save to Firestore, check watchlists.

        Args:
            game: Game to process

        Returns:
            dict: Processing statistics or None if failed
        """
        print(f"[Price Poller] Processing game: {game.title}")

        # Fetch current price using adapters
        current_price = await self._fetch_price(game)

        if not current_price:
            print(f"[Price Poller] Could not fetch price for {game.title}")
            return None

        # Get previous price
        previous_price = self._get_latest_price(game)

        # Save current price to Firestore
        self._save_price(game, current_price)

        # Check for price drops and create notifications
        notifications_created = 0
        if self._should_notify(current_price, previous_price):
            notifications_created = await self._create_notifications(
                game, current_price, previous_price
            )

        return {
            "game_id": game.id,
            "price": current_price.price,
            "notifications": notifications_created,
        }

    async def _fetch_price(self, game: Game) -> Optional[Price]:
        """
        Fetch price for a game using configured adapters.

        Tries adapters in order until one returns a valid price.

        Args:
            game: Game to fetch price for

        Returns:
            Price object or None if all adapters fail
        """
        for adapter in self.adapters:
            try:
                price = await adapter.get_price(game)
                if price:
                    print(
                        f"[Price Poller] Got price from {adapter.name}: ${price.price:.2f}"
                    )
                    return price
            except Exception as e:
                print(f"[Price Poller] Adapter {adapter.name} failed: {e}")
                continue

        return None

    def _get_latest_price(self, game: Game) -> Optional[Price]:
        """
        Get the most recent price for a game from Firestore.

        Args:
            game: Game to get price for

        Returns:
            Price object or None if no previous price exists
        """
        try:
            prices_ref = (
                self.db.collection(GAMES_COLLECTION)
                .document(game.id)
                .collection(PRICES_SUBCOLLECTION)
            )

            # Get most recent price
            docs = prices_ref.order_by(
                "last_checked_at", direction=firestore.Query.DESCENDING
            ).limit(1).stream()

            for doc in docs:
                return Price.from_dict(doc.to_dict())

            return None
        except Exception as e:
            print(f"[Price Poller] Error fetching previous price: {e}")
            return None

    def _save_price(self, game: Game, price: Price):
        """
        Save price to Firestore.

        Args:
            game: Game the price belongs to
            price: Price to save
        """
        try:
            prices_ref = (
                self.db.collection(GAMES_COLLECTION)
                .document(game.id)
                .collection(PRICES_SUBCOLLECTION)
            )

            # Use timestamp as document ID for easy chronological ordering
            doc_id = price.last_checked_at.strftime("%Y%m%d_%H%M%S")
            prices_ref.document(doc_id).set(price.to_dict())

            print(f"[Price Poller] Saved price for {game.title}: ${price.price:.2f}")
        except Exception as e:
            print(f"[Price Poller] Error saving price: {e}")
            raise

    def _should_notify(
        self, current_price: Price, previous_price: Optional[Price]
    ) -> bool:
        """
        Determine if notifications should be created for this price update.

        Args:
            current_price: Current price
            previous_price: Previous price or None

        Returns:
            bool: True if notifications should be created
        """
        # Always notify if game went on sale
        if current_price.on_sale and (
            not previous_price or not previous_price.on_sale
        ):
            return True

        # Notify if significant price drop (10% or more)
        if previous_price and current_price.is_significant_drop(
            previous_price.price, threshold_percent=10.0
        ):
            return True

        return False

    async def _create_notifications(
        self, game: Game, current_price: Price, previous_price: Optional[Price]
    ) -> int:
        """
        Create notifications for users watching this game.

        Args:
            game: Game with price change
            current_price: Current price
            previous_price: Previous price or None

        Returns:
            int: Number of notifications created
        """
        # Fetch all watchlists
        watchlists = self._fetch_all_watchlists()

        notifications_created = 0
        batch = self.db.batch()
        notifications_ref = self.db.collection(NOTIFICATIONS_COLLECTION)

        for watchlist in watchlists:
            watchlist_item = watchlist.get_item(game.id)

            if not watchlist_item:
                continue

            # Check if user's criteria are met
            should_notify = watchlist_item.should_notify(
                current_price.price, current_price.discount_percent
            )

            # Also notify on general price drops
            if not should_notify and self._should_notify(current_price, previous_price):
                should_notify = True

            if should_notify:
                notification = Notification(
                    user_id=watchlist.user_id,
                    game_id=game.id,
                    game_title=game.title,
                    old_price=previous_price.price if previous_price else None,
                    new_price=current_price.price,
                    discount_percent=current_price.discount_percent,
                    timestamp=datetime.utcnow(),
                    type="price_drop",
                    read=False,
                )

                # Add to batch
                doc_ref = notifications_ref.document()
                batch.set(doc_ref, notification.to_dict())
                notifications_created += 1

                print(
                    f"[Price Poller] Creating notification for user {watchlist.user_id}"
                )

        # Commit batch
        if notifications_created > 0:
            batch.commit()
            print(f"[Price Poller] Created {notifications_created} notifications")

        return notifications_created

    def _fetch_all_watchlists(self) -> List[Watchlist]:
        """
        Fetch all watchlists from Firestore.

        Returns:
            List[Watchlist]: List of all watchlists
        """
        try:
            watchlists_ref = self.db.collection(WATCHLISTS_COLLECTION)
            docs = watchlists_ref.stream()

            watchlists = []
            for doc in docs:
                data = doc.to_dict()
                watchlists.append(Watchlist.from_dict(data))

            return watchlists
        except Exception as e:
            print(f"[Price Poller] Error fetching watchlists: {e}")
            return []
