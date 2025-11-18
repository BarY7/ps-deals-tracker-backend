.PHONY: help install test lint clean emulator seed run

help:
	@echo "PlayStation Game Price Tracker - Backend"
	@echo ""
	@echo "Available commands:"
	@echo "  make install    Install dependencies"
	@echo "  make test       Run tests"
	@echo "  make lint       Run linter (if configured)"
	@echo "  make emulator   Start Firestore emulator"
	@echo "  make seed       Seed test data"
	@echo "  make run        Run price update"
	@echo "  make clean      Clean up generated files"

install:
	pip install -r requirements.txt

test:
	pytest -v

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term

emulator:
	@echo "Starting Firestore emulator..."
	@echo "Access UI at http://localhost:4000"
	firebase emulators:start --only firestore

seed:
	@echo "Seeding test data..."
	@echo "Make sure FIRESTORE_EMULATOR_HOST is set"
	python scripts/seed_data.py

run:
	@echo "Running price update..."
	@echo "Make sure FIRESTORE_EMULATOR_HOST is set"
	python scripts/run_price_update.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage

lint:
	@echo "Linting not configured. Install flake8 or black for linting."
