@echo off
REM Local Testing Script for PlayStation Game Price Tracker (Windows)
REM This script automates the local testing process

echo ==========================================
echo PS Game Price Tracker - Local Testing
echo ==========================================
echo.

REM Step 1: Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11+
    exit /b 1
)
echo [OK] Python found
echo.

REM Step 2: Install dependencies
echo [2/5] Installing dependencies...
pip install -r requirements.txt
echo.

REM Step 3: Set environment variables
echo [3/5] Setting environment variables...
set FIRESTORE_EMULATOR_HOST=localhost:8080
set GCP_PROJECT=ps-deals-tracker
set USE_MOCK_ADAPTER=true
set BATCH_SIZE=10

echo [OK] Environment configured
echo   FIRESTORE_EMULATOR_HOST=%FIRESTORE_EMULATOR_HOST%
echo   GCP_PROJECT=%GCP_PROJECT%
echo   USE_MOCK_ADAPTER=%USE_MOCK_ADAPTER%
echo.

REM Step 4: Instructions for Firebase emulator
echo [4/5] Firebase Emulator Setup
echo.
echo IMPORTANT: You need to start the Firebase emulator manually:
echo   1. Open a NEW command prompt/terminal
echo   2. Navigate to this directory
echo   3. Run: firebase emulators:start --only firestore
echo   4. Wait until you see "All emulators ready!"
echo   5. Return to this window and press any key to continue
echo.
pause

REM Step 5: Seed data and run update
echo [5/5] Seeding test data...
python scripts/seed_data.py
echo.

echo Running price update...
python scripts/run_price_update.py
echo.

REM Summary
echo ==========================================
echo Local Testing Setup Complete!
echo ==========================================
echo.
echo What was created:
echo   - 8 PlayStation games in Firestore
echo   - 2 test user watchlists
echo   - Initial price data for all games
echo.
echo Next steps:
echo   1. View data in Firestore UI: http://localhost:4000/firestore
echo   2. Run price update again to simulate price changes:
echo      python scripts/run_price_update.py
echo   3. Check 'notifications' collection for price drop alerts
echo.
echo Press any key to exit...
pause >nul
