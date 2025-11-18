"""
Manually run the price update script for testing.

This script allows you to run the price update locally to test the full workflow.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import main


if __name__ == "__main__":
    print("Running price update manually...")
    print("Make sure FIRESTORE_EMULATOR_HOST is set for local testing")
    print(f"Current FIRESTORE_EMULATOR_HOST: {os.getenv('FIRESTORE_EMULATOR_HOST', 'Not set')}")
    print("")

    main()
