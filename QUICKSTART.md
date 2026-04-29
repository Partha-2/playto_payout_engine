# Quick Start Guide

Get the Playto Payout Engine running in minutes.

## Option 1: Docker Compose (Recommended for Local Development)

### Prerequisites
- Docker and Docker Compose installed

### Commands
```bash
# Start all services
docker-compose up

# In another terminal, seed the database
docker-compose exec backend python manage.py seed_data

# Access services
Backend:  http://localhost:8000/api/v1/merchants/
Frontend: http://localhost:5173
```

## Option 2: Manual Setup (Linux/Mac)

### Prerequisites
- Python 3.10+
- PostgreSQL 13+
- Redis 6+
- Node.js 18+

### Backend Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../.env.example .env

# Update DATABASE_URL in .env to your local PostgreSQL
# Example: DATABASE_URL=postgresql://user:password@localhost:5432/playto_db

# Run migrations
python manage.py migrate

# Seed initial data
python manage.py seed_data

# Start Django development server (Terminal 1)
python manage.py runserver

# Start Celery worker (Terminal 2)
celery -A payout_service worker --loglevel=info

# Start Celery beat scheduler (Terminal 3)
celery -A payout_service beat --loglevel=info
```

### Frontend Setup
```bash
# In new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Verify Everything Works
```bash
# Get list of merchants
curl http://localhost:8000/api/v1/merchants/

# Expected response:
# [{"id": 1, "name": "Alice Agencies", "balance_paise": 123456, ...}, ...]

# Create a payout
curl -X POST http://localhost:8000/api/v1/payouts \
  -H "Idempotency-Key: $(uuidgen)" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_id": 1,
    "amount_paise": 5000,
    "bank_account_id": "BANK-IND-9921"
  }'

# Expected response:
# {"id": 1, "status": "PENDING", "amount_paise": 5000, ...}
```

## Access Points

- **API Documentation**: http://localhost:8000/admin/ (Django Admin)
- **Merchants Endpoint**: http://localhost:8000/api/v1/merchants/
- **Payouts Endpoint**: http://localhost:8000/api/v1/payouts (POST only)
- **Frontend Dashboard**: http://localhost:5173/
- **Celery Flower** (optional): `pip install flower` then `celery -A payout_service events`

## Testing

### Run all tests
```bash
cd backend
python manage.py test core.tests -v 2
```

### Run specific test
```bash
python manage.py test core.tests.PayoutIntegrityTest.test_concurrency_protection -v 2
```

## Common Issues

### "Port already in use"
```bash
# Find process using port
lsof -i :8000
# Kill process
kill -9 <PID>
```

### "Database does not exist"
```bash
# Create database manually
createdb playto_db
```

### "psycopg2 not found"
```bash
# On Mac with M1:
LDFLAGS=-L/opt/homebrew/opt/openssl@1.1/lib CPPFLAGS=-I/opt/homebrew/opt/openssl@1.1/include pip install psycopg2

# On Ubuntu/Debian:
sudo apt-get install postgresql-client libpq-dev
pip install psycopg2
```

## Next Steps

1. Explore the codebase in `backend/core/` to understand the models and views
2. Read [EXPLAINER.md](backend/EXPLAINER.md) for technical deep-dive
3. Review tests in `backend/core/tests.py` for testing patterns
4. Deploy to Render or Railway using [DEPLOYMENT.md](DEPLOYMENT.md)
