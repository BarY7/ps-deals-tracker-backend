# Local Testing Guide

This guide shows you exactly how to test the PlayStation game price tracker backend locally before deploying to production.

## Prerequisites

- **Python 3.11+** installed
- **Node.js and npm** installed (for Firebase CLI)
- **Firebase CLI** installed: `npm install -g firebase-tools`

## Quick Start (Automated)

### Linux/macOS
```bash
chmod +x test_local.sh
./test_local.sh
```

### Windows
```cmd
test_local.bat
```

The automated script will:
1. Check dependencies
2. Start Firestore emulator
3. Seed test data (8 games, 2 watchlists)
4. Run initial price update
5. Show you where to view results

---

## Manual Testing (Step-by-Step)

If you prefer to run commands manually, follow these steps:

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed google-cloud-firestore-2.14.0 httpx-0.26.0 ...
```

---

### Step 2: Start Firestore Emulator

**Open a NEW terminal window** and run:

```bash
firebase emulators:start --only firestore
```

**Expected output:**
```
┌─────────────────────────────────────────────────────────────┐
│ ✔  All emulators ready! It is now safe to connect your app. │
│ i  View Emulator UI at http://127.0.0.1:4000                │
└─────────────────────────────────────────────────────────────┘

┌───────────┬────────────────┬─────────────────────────────────┐
│ Emulator  │ Host:Port      │ View in Emulator UI             │
├───────────┼────────────────┼─────────────────────────────────┤
│ Firestore │ localhost:8080 │ http://127.0.0.1:4000/firestore │
└───────────┴────────────────┴─────────────────────────────────┘
```

**Keep this terminal open!** The emulator must stay running.

**Verify emulator is running:**
```bash
curl http://localhost:8080
```

---

### Step 3: Set Environment Variables

**In your ORIGINAL terminal**, set these variables:

#### Linux/macOS:
```bash
export FIRESTORE_EMULATOR_HOST="localhost:8080"
export GCP_PROJECT="ps-deals-tracker"
export USE_MOCK_ADAPTER="true"
```

#### Windows (CMD):
```cmd
set FIRESTORE_EMULATOR_HOST=localhost:8080
set GCP_PROJECT=ps-deals-tracker
set USE_MOCK_ADAPTER=true
```

#### Windows (PowerShell):
```powershell
$env:FIRESTORE_EMULATOR_HOST="localhost:8080"
$env:GCP_PROJECT="ps-deals-tracker"
$env:USE_MOCK_ADAPTER="true"
```

**Verify variables are set:**
```bash
# Linux/macOS
echo $FIRESTORE_EMULATOR_HOST

# Windows CMD
echo %FIRESTORE_EMULATOR_HOST%

# Windows PowerShell
echo $env:FIRESTORE_EMULATOR_HOST
```

Should print: `localhost:8080`

---

### Step 4: Seed Test Data

```bash
python scripts/seed_data.py
```

**Expected output:**
```
============================================================
[Seed] Starting data seeding...
[Seed] Make sure FIRESTORE_EMULATOR_HOST is set for local testing
[Seed] Current FIRESTORE_EMULATOR_HOST: localhost:8080
============================================================
[Firestore] Using emulator at localhost:8080
[Seed] Adding sample games...
[Seed] Added game: God of War Ragnarök
[Seed] Added game: Marvel's Spider-Man 2
[Seed] Added game: The Last of Us Part II
[Seed] Added game: Horizon Forbidden West
[Seed] Added game: Elden Ring
[Seed] Added game: Ratchet & Clank: Rift Apart
[Seed] Added game: Returnal
[Seed] Added game: Ghost of Tsushima
[Seed] Successfully added 8 games
[Seed] Adding sample watchlists...
[Seed] Added watchlist for test_user_1 with 3 games
[Seed] Added watchlist for test_user_2 with 2 games
[Seed] Successfully added 2 watchlists
============================================================
[Seed] Data seeding completed successfully!
============================================================
```

**What was created:**
- ✅ 8 games in `games` collection
- ✅ 2 watchlists in `watchlists` collection

---

### Step 5: View Seeded Data

Open your browser and go to:
```
http://localhost:4000/firestore
```

You should see:
- **games** collection with 8 documents
- **watchlists** collection with 2 documents
- No **prices** or **notifications** yet (these come from price updates)

---

### Step 6: Run First Price Update

```bash
python scripts/run_price_update.py
```

**Expected output:**
```
Running price update manually...
Make sure FIRESTORE_EMULATOR_HOST is set for local testing
Current FIRESTORE_EMULATOR_HOST: localhost:8080

============================================================
[Main] Starting price update at 2024-01-15T10:30:00.000000
============================================================
[Firestore] Using emulator at localhost:8080
[Main] Using adapters: ['MockPriceAdapter']
[Price Poller] Starting price polling run...
[Price Poller] Found 8 games to process
[Price Poller] Processing game: God of War Ragnarök
[Price Poller] Got price from MockPriceAdapter: $59.99
[Price Poller] Saved price for God of War Ragnarök: $59.99
[Price Poller] Processing game: Marvel's Spider-Man 2
[Price Poller] Got price from MockPriceAdapter: $69.99
[Price Poller] Saved price for Marvel's Spider-Man 2: $69.99
...
[Price Poller] Polling complete in 2.35s
[Price Poller] Stats: {'total_games': 8, 'successful': 8, 'failed': 0, 'notifications_created': 0}
============================================================
[Main] Price update completed successfully
[Main] Final stats: {...}
============================================================
```

**What happened:**
- ✅ Fetched prices for all 8 games
- ✅ Saved prices to `games/{game_id}/prices` subcollection
- ✅ No notifications yet (this is the baseline - no previous prices to compare)

---

### Step 7: View Price Data

Refresh the Firestore UI: http://localhost:4000/firestore

1. Click on any game document (e.g., `god-of-war-ragnarok`)
2. You'll see a **prices** subcollection
3. Click it to see the price document with:
   - `price`: Current price (e.g., 59.99)
   - `original_price`: Base price (e.g., 69.99)
   - `discount_percent`: Discount % (e.g., 14)
   - `on_sale`: true/false
   - `last_checked_at`: Timestamp

---

### Step 8: Run Second Price Update (Trigger Notifications)

```bash
python scripts/run_price_update.py
```

**This time you might see notifications:**
```
[Price Poller] Processing game: God of War Ragnarök
[Price Poller] Got price from MockPriceAdapter: $49.99
[Price Poller] Saved price for God of War Ragnarök: $49.99
[Price Poller] Creating notification for user test_user_1
[Price Poller] Created 1 notifications
```

**What triggers a notification:**
1. **Game goes on sale** - `on_sale` changes from false to true
2. **Significant price drop** - Price drops ≥10% from previous check
3. **Watchlist match** - Price meets user's desired_price or desired_discount_pct

---

### Step 9: View Notifications

Refresh Firestore UI and check the **notifications** collection.

You should see documents like:
```json
{
  "user_id": "test_user_1",
  "game_id": "god-of-war-ragnarok",
  "game_title": "God of War Ragnarök",
  "old_price": 69.99,
  "new_price": 49.99,
  "discount_percent": 28,
  "timestamp": "2024-01-15T10:32:00Z",
  "type": "price_drop",
  "read": false
}
```

---

### Step 10: Run Multiple Updates (Force Notifications)

To ensure you see price changes and notifications:

```bash
# Run 5 price updates with 2-second delays
for i in {1..5}; do
  echo "--- Run $i ---"
  python scripts/run_price_update.py
  sleep 2
done
```

**Windows CMD:**
```cmd
for /L %i in (1,1,5) do (
  echo --- Run %i ---
  python scripts/run_price_update.py
  timeout /t 2
)
```

After 5 runs, you should definitely see notifications in the `notifications` collection.

---

## What to Test

### ✅ Games Collection
- [ ] 8 games present
- [ ] Each has id, title, platform, genres, etc.
- [ ] Each has a `prices` subcollection

### ✅ Prices Subcollection
- [ ] Multiple price documents (one per update)
- [ ] Prices vary between runs (mock adapter)
- [ ] Some games on sale (on_sale: true)
- [ ] Timestamps are correct

### ✅ Watchlists Collection
- [ ] 2 watchlists (test_user_1, test_user_2)
- [ ] Each has games array with desired_price/desired_discount_pct
- [ ] User 1 watching: God of War, Spider-Man 2, Elden Ring
- [ ] User 2 watching: Horizon, Returnal

### ✅ Notifications Collection
- [ ] Notifications created when prices drop
- [ ] Contains user_id, game_id, old_price, new_price
- [ ] Type is "price_drop"
- [ ] Read is false by default

---

## Running Tests

Run the pytest test suite:

```bash
pytest -v
```

**Expected output:**
```
tests/test_adapters.py::TestMockPriceAdapter::test_adapter_name PASSED
tests/test_adapters.py::TestMockPriceAdapter::test_get_price_returns_price PASSED
tests/test_models.py::TestGame::test_game_creation PASSED
tests/test_models.py::TestPrice::test_is_significant_drop PASSED
tests/test_utils.py::TestSlugify::test_basic_slugify PASSED
...

======================== 25 passed in 3.45s ========================
```

**With coverage:**
```bash
pytest --cov=app --cov-report=term
```

---

## Troubleshooting

### Emulator Not Found
```
Error: firebase: command not found
```
**Fix:** Install Firebase CLI
```bash
npm install -g firebase-tools
```

### Import Errors
```
ModuleNotFoundError: No module named 'google.cloud'
```
**Fix:** Install dependencies
```bash
pip install -r requirements.txt
```

### Connection Refused
```
[Errno 111] Connection refused
```
**Fix:** Make sure emulator is running and environment variable is set
```bash
# Check if emulator is running
curl http://localhost:8080

# Check environment variable
echo $FIRESTORE_EMULATOR_HOST  # Should be "localhost:8080"
```

### No Notifications Created
**Reasons:**
1. First run has no previous prices to compare
2. Price changes were too small (<10% drop)
3. Watchlist criteria not met

**Fix:** Run price update multiple times:
```bash
for i in {1..5}; do python scripts/run_price_update.py; sleep 2; done
```

### Emulator Port Already in Use
```
Error: Port 8080 is already in use
```
**Fix:** Kill existing emulator
```bash
# Linux/macOS
pkill -f "firebase.*emulators"

# Windows
taskkill /F /IM firebase.exe
```

---

## Clean Up

### Stop the Emulator
In the terminal running the emulator, press `Ctrl+C`.

### Clear All Data
```bash
# Stop emulator first, then delete emulator data
rm -rf .firebase/
```

### Deactivate Virtual Environment (if using)
```bash
deactivate
```

---

## Summary

**One-command test (Linux/macOS):**
```bash
./test_local.sh
```

**Manual test commands:**
```bash
# Terminal 1: Start emulator
firebase emulators:start --only firestore

# Terminal 2: Set env vars, seed data, run updates
export FIRESTORE_EMULATOR_HOST="localhost:8080"
export GCP_PROJECT="ps-deals-tracker"
export USE_MOCK_ADAPTER="true"

python scripts/seed_data.py
python scripts/run_price_update.py
python scripts/run_price_update.py  # Run again to trigger notifications

# View results
open http://localhost:4000/firestore
```

**Expected results:**
- ✅ 8 games with price history
- ✅ 2 watchlists
- ✅ Price drop notifications

You're now ready to deploy to production! 🚀
