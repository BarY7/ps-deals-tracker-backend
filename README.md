# PlayStation Game Price Tracker - Backend

A serverless backend for tracking PlayStation game prices and notifying users of price drops. This backend runs scheduled scripts that update Firestore with the latest price data. The Flutter frontend reads data directly from Firestore - there is no REST API.

## Features

- 🎮 Track PlayStation game prices (PS4, PS5)
- 📊 Historical price tracking with Firestore
- 🔔 Automatic price drop notifications
- 👀 User watchlists with custom price alerts
- 🔄 Scheduled price polling via Cloud Scheduler
- 🧪 Local development with Firestore emulator
- 📦 Serverless architecture (Cloud Functions/Cloud Run)

## 🚀 Quick Start - Local Testing

**Want to test locally before deploying? Start here!**

### Automated (Recommended)
```bash
# Linux/macOS
chmod +x test_local.sh
./test_local.sh

# Windows
test_local.bat
```

### Manual Commands
```bash
# 1. Start Firestore emulator (in separate terminal)
firebase emulators:start --only firestore

# 2. Set environment variables
export FIRESTORE_EMULATOR_HOST="localhost:8080"
export GCP_PROJECT="ps-deals-tracker"
export USE_MOCK_ADAPTER="true"

# 3. Seed data and run price update
python scripts/seed_data.py
python scripts/run_price_update.py

# 4. View results at http://localhost:4000/firestore
```

**📖 For detailed testing instructions, see [TESTING.md](TESTING.md)**

---

## Tech Stack

- **Python 3.11+**
- **Google Cloud Firestore** (Native Mode)
- **google-cloud-firestore** SDK
- **HTTPX** for async HTTP requests
- **asyncio** for concurrent price fetching
- **pytest** for testing

## Project Structure

```
ps-deals-tracker-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Main entrypoint for scheduled script
│   ├── adapters/            # Price source adapters
│   │   ├── base_adapter.py
│   │   ├── mock_adapter.py  # Mock data for testing
│   │   └── psn_adapter.py   # PSN Store API (stub)
│   ├── db/                  # Firestore initialization
│   │   └── firestore.py
│   ├── models/              # Data models
│   │   ├── game.py
│   │   ├── price.py
│   │   ├── watchlist.py
│   │   └── notification.py
│   ├── services/            # Business logic
│   │   └── price_poller.py
│   └── utils/               # Utility functions
│       └── slugify.py
├── scripts/
│   ├── seed_data.py         # Seed test data
│   └── run_price_update.py  # Manual price update
├── tests/                   # Pytest tests
│   ├── test_models.py
│   ├── test_adapters.py
│   ├── test_utils.py
│   └── test_price_poller.py
├── requirements.txt
├── pytest.ini
└── README.md
```

## Data Model

### Firestore Collections

#### 1. `games` collection
Each game document contains:
- `id` (string) - Unique slug identifier
- `title` (string) - Game title
- `platform` (string) - "PS4", "PS5", or "PS4/PS5"
- `psn_id` (string, optional) - PlayStation Store ID
- `release_date` (string) - ISO date string
- `genres` (array) - List of genre strings
- `image_url` (string) - Cover image URL
- `description` (string) - Game description
- `created_at` (timestamp)
- `updated_at` (timestamp)

**Subcollection: `prices`**
Each price document contains:
- `price` (float) - Current price
- `original_price` (float) - Original/base price
- `discount_percent` (int) - Discount percentage
- `on_sale` (boolean) - Whether game is on sale
- `last_checked_at` (timestamp) - When price was checked
- `currency` (string) - Currency code (e.g., "USD")

#### 2. `watchlists` collection
Each watchlist document (keyed by user_id) contains:
- `user_id` (string) - User identifier
- `games` (array) - Array of watchlist items:
  - `game_id` (string)
  - `desired_price` (float, optional) - Alert when price drops below
  - `desired_discount_pct` (int, optional) - Alert when discount exceeds
  - `created_at` (timestamp)
- `created_at` (timestamp)
- `updated_at` (timestamp)

#### 3. `notifications` collection
Each notification document contains:
- `user_id` (string) - User to notify
- `game_id` (string) - Game that triggered notification
- `game_title` (string) - Game title for display
- `old_price` (float, optional) - Previous price
- `new_price` (float) - New price
- `discount_percent` (int) - Current discount
- `timestamp` (timestamp) - When notification was created
- `type` (string) - "price_drop"
- `read` (boolean) - Whether user has seen notification

## Installation

### Prerequisites

- Python 3.11 or higher
- Google Cloud SDK (for production deployment)
- Firestore emulator (for local development)

### 1. Clone the repository

```bash
git clone <repository-url>
cd ps-deals-tracker-backend
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Or using a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Local Development

### 1. Start Firestore Emulator

Install the Firebase CLI and start the emulator:

```bash
# Install Firebase CLI (if not already installed)
npm install -g firebase-tools

# Initialize Firebase (first time only)
firebase init emulators

# Start Firestore emulator
firebase emulators:start --only firestore
```

The emulator will start on `localhost:8080` by default.

### 2. Set environment variables

```bash
export FIRESTORE_EMULATOR_HOST="localhost:8080"
export GCP_PROJECT="ps-deals-tracker"
export USE_MOCK_ADAPTER="true"
```

On Windows (CMD):
```cmd
set FIRESTORE_EMULATOR_HOST=localhost:8080
set GCP_PROJECT=ps-deals-tracker
set USE_MOCK_ADAPTER=true
```

On Windows (PowerShell):
```powershell
$env:FIRESTORE_EMULATOR_HOST="localhost:8080"
$env:GCP_PROJECT="ps-deals-tracker"
$env:USE_MOCK_ADAPTER="true"
```

### 3. Seed test data

Populate Firestore with sample games and watchlists:

```bash
python scripts/seed_data.py
```

This will add:
- 8 sample PlayStation games
- 2 test user watchlists

### 4. Run price update manually

```bash
python scripts/run_price_update.py
```

Or directly:

```bash
python -m app.main
```

This will:
1. Fetch prices for all games using the mock adapter
2. Save prices to Firestore
3. Check watchlists for matches
4. Create notifications for price drops

### 5. Verify results

You can view the data in the Firestore emulator UI:
```
http://localhost:4000/firestore
```

## Testing

Run all tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app --cov-report=html
```

Run specific test file:

```bash
pytest tests/test_models.py
```

Run tests with verbose output:

```bash
pytest -v
```

## Simulating a Price Drop

To test price drop notifications:

1. **Start the Firestore emulator** and **seed data**:
   ```bash
   firebase emulators:start --only firestore
   export FIRESTORE_EMULATOR_HOST="localhost:8080"
   python scripts/seed_data.py
   ```

2. **Run the price update** to establish baseline prices:
   ```bash
   python scripts/run_price_update.py
   ```

3. **Check the `prices` subcollection** in the Firestore emulator UI to see current prices

4. **Run the price update again**:
   ```bash
   python scripts/run_price_update.py
   ```

5. **Check the `notifications` collection** to see if any price drop notifications were created

The mock adapter randomly generates prices, so you may need to run the update multiple times to see a significant price drop that triggers a notification.

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FIRESTORE_EMULATOR_HOST` | Firestore emulator address | - | Local dev only |
| `GCP_PROJECT` | Google Cloud project ID | `ps-deals-tracker` | Yes |
| `USE_MOCK_ADAPTER` | Use mock adapter instead of PSN | `true` | No |
| `PSN_API_KEY` | API key for PSN adapter | - | Production only |
| `BATCH_SIZE` | Games to process concurrently | `10` | No |

## Deployment

### Option 1: Cloud Functions (Recommended)

1. **Create a Cloud Function**:
   ```bash
   gcloud functions deploy ps-price-tracker \
     --runtime python311 \
     --trigger-http \
     --entry-point cloud_function_handler \
     --source . \
     --set-env-vars GCP_PROJECT=your-project-id,USE_MOCK_ADAPTER=false
   ```

2. **Set up Cloud Scheduler**:
   ```bash
   gcloud scheduler jobs create http price-update-job \
     --schedule="0 */6 * * *" \
     --uri="https://REGION-PROJECT_ID.cloudfunctions.net/ps-price-tracker" \
     --http-method=POST
   ```

This will run the price update every 6 hours.

### Option 2: Cloud Run

1. **Create a Dockerfile**:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python", "-m", "app.main"]
   ```

2. **Build and deploy**:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/ps-price-tracker
   gcloud run deploy ps-price-tracker \
     --image gcr.io/PROJECT_ID/ps-price-tracker \
     --platform managed
   ```

3. **Set up Cloud Scheduler** to trigger the Cloud Run service

### Option 3: Cloud Scheduler with Pub/Sub

1. **Deploy the scheduled handler**:
   ```bash
   gcloud functions deploy ps-price-tracker-scheduled \
     --runtime python311 \
     --trigger-topic price-update \
     --entry-point scheduled_handler \
     --source .
   ```

2. **Create scheduler job**:
   ```bash
   gcloud scheduler jobs create pubsub price-update-job \
     --schedule="0 */6 * * *" \
     --topic=price-update \
     --message-body="{}"
   ```

## Price Source Adapters

### Mock Adapter (MockPriceAdapter)

Used for local development and testing. Generates realistic random prices with configurable sale probability.

**Features:**
- Platform-specific price ranges (PS4: $29.99-$59.99, PS5: $49.99-$69.99)
- Configurable sale probability
- Random discount percentages (10%-75%)
- 5% simulated failure rate

### PSN Adapter (PSNPriceAdapter)

**STUB IMPLEMENTATION** - Requires actual PSN Store API integration.

To implement:
1. Obtain official PlayStation Store API access from Sony, OR
2. Reverse engineer the PSN Store API (use at own risk), OR
3. Use a third-party PSN price data service

Replace the `_fetch_from_api()` method in `app/adapters/psn_adapter.py` with actual API calls.

### Creating Custom Adapters

Extend `PriceSourceAdapter` base class:

```python
from app.adapters.base_adapter import PriceSourceAdapter
from app.models import Price

class MyCustomAdapter(PriceSourceAdapter):
    @property
    def name(self) -> str:
        return "MyCustomAdapter"

    async def get_price(self, game: Game) -> Optional[Price]:
        # Implement price fetching logic
        pass
```

## Notification Logic

Notifications are created when:

1. **Game goes on sale** - `on_sale` changes from `false` to `true`
2. **Significant price drop** - Price drops by ≥10% from previous check
3. **Watchlist criteria met**:
   - Price drops to or below user's `desired_price`, OR
   - Discount reaches or exceeds user's `desired_discount_pct`

## Troubleshooting

### Firestore permission errors

Make sure you're authenticated:
```bash
gcloud auth application-default login
```

### Tests failing with import errors

Make sure you're in the project root and the `app` package is in your Python path:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Emulator connection errors

Verify the emulator is running:
```bash
curl http://localhost:8080
```

Check the environment variable is set:
```bash
echo $FIRESTORE_EMULATOR_HOST
```

### No notifications being created

1. Verify watchlists exist with `desired_price` or `desired_discount_pct` set
2. Check that prices are being saved to the `prices` subcollection
3. Ensure the mock adapter is generating price variations
4. Look for logs in the console output

## Performance Considerations

- **Batch size**: Adjust `BATCH_SIZE` environment variable (default: 10)
- **Concurrent processing**: The service processes games in batches using asyncio
- **Firestore batching**: Notifications are written in batches to minimize writes
- **Rate limiting**: Consider implementing rate limiting for production PSN API usage

## Future Enhancements

- [ ] Implement real PSN Store API integration
- [ ] Add support for multiple regions/currencies
- [ ] Email/push notification delivery
- [ ] Price prediction using historical data
- [ ] Admin dashboard for monitoring
- [ ] Webhook support for external integrations
- [ ] Support for other platforms (Xbox, Steam, etc.)

## License

[Your License Here]

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Support

For issues or questions, please open a GitHub issue.
