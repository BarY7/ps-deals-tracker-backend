"""
Main entrypoint for the PlayStation game price tracker scheduled script.

This script is designed to be run by Cloud Scheduler or as a cron job.
It fetches current prices for all games and creates notifications for price drops.
"""

import asyncio
import os
import sys
from datetime import datetime

from app.adapters import MockPriceAdapter, PSNPriceAdapter
from app.services import PricePollingService
from app.db import close_clients


async def run_price_update():
    """
    Main function to run price updates.

    This function:
    1. Initializes price source adapters
    2. Creates price polling service
    3. Polls all games for price updates
    4. Creates notifications for price drops
    """
    print("=" * 60)
    print(f"[Main] Starting price update at {datetime.utcnow().isoformat()}")
    print("=" * 60)

    # Initialize adapters
    # Try PSN adapter first, fall back to mock for local testing
    use_mock = os.getenv("USE_MOCK_ADAPTER", "true").lower() == "true"

    adapters = []

    if not use_mock:
        psn_api_key = os.getenv("PSN_API_KEY")
        adapters.append(PSNPriceAdapter(api_key=psn_api_key))

    # Always include mock adapter as fallback
    adapters.append(MockPriceAdapter(enable_sales=True, sale_probability=0.3))

    print(f"[Main] Using adapters: {[adapter.name for adapter in adapters]}")

    # Create polling service
    batch_size = int(os.getenv("BATCH_SIZE", "10"))
    service = PricePollingService(adapters=adapters, batch_size=batch_size)

    # Run price polling
    try:
        stats = await service.poll_all_games()

        print("=" * 60)
        print("[Main] Price update completed successfully")
        print(f"[Main] Final stats: {stats}")
        print("=" * 60)

        return stats

    except Exception as e:
        print(f"[Main] Error during price update: {e}")
        import traceback

        traceback.print_exc()
        raise

    finally:
        # Clean up Firestore connections
        close_clients()


def main():
    """
    Synchronous entrypoint for the script.

    Can be called from Cloud Functions, Cloud Run, or as a standalone script.
    """
    try:
        stats = asyncio.run(run_price_update())
        print(f"[Main] Exiting with stats: {stats}")
        return stats

    except Exception as e:
        print(f"[Main] Fatal error: {e}")
        sys.exit(1)


# Cloud Functions entrypoint
def cloud_function_handler(request=None):
    """
    Entrypoint for Google Cloud Functions.

    Args:
        request: Flask request object (unused but required by Cloud Functions)

    Returns:
        tuple: (response_body, status_code)
    """
    try:
        stats = main()
        return ({"status": "success", "stats": stats}, 200)

    except Exception as e:
        return ({"status": "error", "message": str(e)}, 500)


# Cloud Run / Cloud Scheduler entrypoint
def scheduled_handler(event=None, context=None):
    """
    Entrypoint for Cloud Scheduler via Pub/Sub trigger.

    Args:
        event: Pub/Sub event data
        context: Event context

    Returns:
        dict: Response with status
    """
    try:
        stats = main()
        return {"status": "success", "stats": stats}

    except Exception as e:
        print(f"[Main] Error in scheduled handler: {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    """Run the script directly from command line."""
    main()
