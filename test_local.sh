#!/bin/bash

# Local Testing Script for PlayStation Game Price Tracker
# This script automates the local testing process

set -e  # Exit on error

echo "=========================================="
echo "PS Game Price Tracker - Local Testing"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check if Firebase CLI is installed
echo -e "${YELLOW}[1/6] Checking Firebase CLI...${NC}"
if ! command -v firebase &> /dev/null
then
    echo "Firebase CLI not found. Please install it:"
    echo "  npm install -g firebase-tools"
    exit 1
fi
echo -e "${GREEN}✓ Firebase CLI found${NC}"
echo ""

# Step 2: Check Python dependencies
echo -e "${YELLOW}[2/6] Checking Python dependencies...${NC}"
if ! python -c "import google.cloud.firestore" &> /dev/null
then
    echo "Dependencies not installed. Installing..."
    pip install -r requirements.txt
else
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi
echo ""

# Step 3: Start Firestore emulator in background
echo -e "${YELLOW}[3/6] Starting Firestore emulator...${NC}"
echo "This may take a few seconds..."

# Kill any existing emulator processes
pkill -f "firebase.*emulators" || true

# Start emulator in background
firebase emulators:start --only firestore > /dev/null 2>&1 &
EMULATOR_PID=$!

# Wait for emulator to be ready
echo "Waiting for emulator to start..."
sleep 5

# Check if emulator is running
if ! curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo "Failed to start emulator. Trying again..."
    sleep 5
fi

echo -e "${GREEN}✓ Firestore emulator running${NC}"
echo "  - Firestore: http://localhost:8080"
echo "  - UI: http://localhost:4000/firestore"
echo ""

# Step 4: Set environment variables
echo -e "${YELLOW}[4/6] Setting environment variables...${NC}"
export FIRESTORE_EMULATOR_HOST="localhost:8080"
export GCP_PROJECT="ps-deals-tracker"
export USE_MOCK_ADAPTER="true"
export BATCH_SIZE="10"

echo -e "${GREEN}✓ Environment configured${NC}"
echo "  FIRESTORE_EMULATOR_HOST=$FIRESTORE_EMULATOR_HOST"
echo "  GCP_PROJECT=$GCP_PROJECT"
echo "  USE_MOCK_ADAPTER=$USE_MOCK_ADAPTER"
echo ""

# Step 5: Seed test data
echo -e "${YELLOW}[5/6] Seeding test data...${NC}"
python scripts/seed_data.py
echo ""

# Step 6: Run price update
echo -e "${YELLOW}[6/6] Running price update (first run)...${NC}"
python scripts/run_price_update.py
echo ""

# Summary
echo "=========================================="
echo -e "${GREEN}Local Testing Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "What was created:"
echo "  ✓ 8 PlayStation games in Firestore"
echo "  ✓ 2 test user watchlists"
echo "  ✓ Initial price data for all games"
echo ""
echo "Next steps:"
echo "  1. View data in Firestore UI: http://localhost:4000/firestore"
echo "  2. Run price update again to simulate price changes:"
echo "     python scripts/run_price_update.py"
echo "  3. Check 'notifications' collection for price drop alerts"
echo ""
echo "To run price updates multiple times (to trigger notifications):"
echo "  for i in {1..5}; do python scripts/run_price_update.py; sleep 2; done"
echo ""
echo "To stop the emulator:"
echo "  kill $EMULATOR_PID"
echo ""
echo "Press Ctrl+C to stop the emulator and exit"
echo ""

# Keep script running (emulator is in background)
wait $EMULATOR_PID
