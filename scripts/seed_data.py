"""
Seed script to populate Firestore with sample data for testing.

Run this script to add sample games and watchlists to your Firestore instance.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db import (
    get_firestore_client,
    GAMES_COLLECTION,
    WATCHLISTS_COLLECTION,
)
from app.models import Game, Watchlist, WatchlistItem
from app.utils import game_id_from_title


def seed_games():
    """Add sample PlayStation games to Firestore."""
    print("[Seed] Adding sample games...")

    db = get_firestore_client()
    games_ref = db.collection(GAMES_COLLECTION)

    sample_games = [
        Game(
            id=game_id_from_title("God of War Ragnarök"),
            title="God of War Ragnarök",
            platform="PS5",
            psn_id="PPSA04521",
            release_date="2022-11-09",
            genres=["Action", "Adventure"],
            image_url="https://image.api.playstation.com/vulcan/ap/rnd/202207/1210/4xJ8XB3bi888QTLZYdl7Oi0s.png",
            description="Kratos and Atreus embark on a mythic journey for answers before Ragnarök arrives.",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        Game(
            id=game_id_from_title("Marvel's Spider-Man 2"),
            title="Marvel's Spider-Man 2",
            platform="PS5",
            psn_id="PPSA05694",
            release_date="2023-10-20",
            genres=["Action", "Adventure"],
            image_url="https://image.api.playstation.com/vulcan/ap/rnd/202306/1219/0f31b4f1f37a8c75e6ce6d1de7aad3b42f02c2e4e1d7c9e3.png",
            description="Spider-Men Peter Parker and Miles Morales face the ultimate test of strength.",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        Game(
            id=game_id_from_title("The Last of Us Part II"),
            title="The Last of Us Part II",
            platform="PS4/PS5",
            psn_id="PPSA01880",
            release_date="2020-06-19",
            genres=["Action", "Adventure", "Survival"],
            image_url="https://image.api.playstation.com/vulcan/img/rnd/202010/2618/Y02ljdBodKFBiziorYgqftLE.png",
            description="Five years after their dangerous journey across the post-pandemic United States.",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        Game(
            id=game_id_from_title("Horizon Forbidden West"),
            title="Horizon Forbidden West",
            platform="PS4/PS5",
            psn_id="PPSA02342",
            release_date="2022-02-18",
            genres=["Action", "RPG"],
            image_url="https://image.api.playstation.com/vulcan/ap/rnd/202107/3100/ki0STHGAkIF06Q9vJfSemfxC.png",
            description="Explore distant lands, fight bigger and more awe-inspiring machines.",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        Game(
            id=game_id_from_title("Elden Ring"),
            title="Elden Ring",
            platform="PS4/PS5",
            psn_id="PPSA03566",
            release_date="2022-02-25",
            genres=["Action", "RPG"],
            image_url="https://image.api.playstation.com/vulcan/ap/rnd/202110/2000/aGhopp3MHppi7kooGE2Dtt8C.png",
            description="A vast world where open fields with a variety of situations and huge dungeons.",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        Game(
            id=game_id_from_title("Ratchet & Clank: Rift Apart"),
            title="Ratchet & Clank: Rift Apart",
            platform="PS5",
            psn_id="PPSA01928",
            release_date="2021-06-11",
            genres=["Action", "Adventure", "Platformer"],
            image_url="https://image.api.playstation.com/vulcan/ap/rnd/202101/2921/DwVkTpqfPh0Q1LugGDP2z3dQ.png",
            description="Blast your way through an interdimensional adventure with Ratchet and Clank.",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        Game(
            id=game_id_from_title("Returnal"),
            title="Returnal",
            platform="PS5",
            psn_id="PPSA01342",
            release_date="2021-04-30",
            genres=["Action", "Roguelike", "Sci-Fi"],
            image_url="https://image.api.playstation.com/vulcan/ap/rnd/202011/1621/cDynOZDMyVJMH3pnlLPzf3cL.png",
            description="Break the cycle of chaos on an alien planet.",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        Game(
            id=game_id_from_title("Ghost of Tsushima"),
            title="Ghost of Tsushima",
            platform="PS4/PS5",
            psn_id="PPSA00854",
            release_date="2020-07-17",
            genres=["Action", "Adventure"],
            image_url="https://image.api.playstation.com/vulcan/ap/rnd/202010/0113/knhS4TQXDH9Yy5AcgB1JrHs8.png",
            description="Forge a new path and wage an unconventional war for the freedom of Tsushima.",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
    ]

    for game in sample_games:
        games_ref.document(game.id).set(game.to_dict())
        print(f"[Seed] Added game: {game.title}")

    print(f"[Seed] Successfully added {len(sample_games)} games")


def seed_watchlists():
    """Add sample watchlists to Firestore."""
    print("[Seed] Adding sample watchlists...")

    db = get_firestore_client()
    watchlists_ref = db.collection(WATCHLISTS_COLLECTION)

    sample_watchlists = [
        Watchlist(
            user_id="test_user_1",
            games=[
                WatchlistItem(
                    game_id=game_id_from_title("God of War Ragnarök"),
                    desired_price=49.99,
                    desired_discount_pct=30,
                    created_at=datetime.utcnow(),
                ),
                WatchlistItem(
                    game_id=game_id_from_title("Marvel's Spider-Man 2"),
                    desired_price=59.99,
                    created_at=datetime.utcnow(),
                ),
                WatchlistItem(
                    game_id=game_id_from_title("Elden Ring"),
                    desired_discount_pct=25,
                    created_at=datetime.utcnow(),
                ),
            ],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        Watchlist(
            user_id="test_user_2",
            games=[
                WatchlistItem(
                    game_id=game_id_from_title("Horizon Forbidden West"),
                    desired_price=39.99,
                    created_at=datetime.utcnow(),
                ),
                WatchlistItem(
                    game_id=game_id_from_title("Returnal"),
                    desired_discount_pct=50,
                    created_at=datetime.utcnow(),
                ),
            ],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
    ]

    for watchlist in sample_watchlists:
        watchlists_ref.document(watchlist.user_id).set(watchlist.to_dict())
        print(
            f"[Seed] Added watchlist for {watchlist.user_id} with {len(watchlist.games)} games"
        )

    print(f"[Seed] Successfully added {len(sample_watchlists)} watchlists")


def main():
    """Main function to seed all data."""
    print("=" * 60)
    print("[Seed] Starting data seeding...")
    print("[Seed] Make sure FIRESTORE_EMULATOR_HOST is set for local testing")
    print(f"[Seed] Current FIRESTORE_EMULATOR_HOST: {os.getenv('FIRESTORE_EMULATOR_HOST', 'Not set')}")
    print("=" * 60)

    try:
        seed_games()
        seed_watchlists()

        print("=" * 60)
        print("[Seed] Data seeding completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"[Seed] Error during seeding: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
