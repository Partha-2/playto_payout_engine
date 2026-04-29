# Playto Payout Engine

A production-grade payout engine for international merchants. Built with Django (Backend) and React (Frontend).

## Core Architecture
- **Money Integrity**: Integer-based ledger (paise) with DB-level aggregation using BigIntegerField.
- **Concurrency**: PostgreSQL row-level locking (`SELECT FOR UPDATE`) to prevent race conditions on overdrawing.
- **Idempotency**: Merchant-scoped UUID keys with response persistence for safe retries up to 24 hours.
- **State Machine**: Strict transition rules (PENDING → PROCESSING → COMPLETED/FAILED).
- **Background Engine**: Celery-based processing with 70% success, 20% failure, 10% hang simulation, automatic retry for stuck payouts after 30s.

## Local Development

### Prerequisites
- Python 3.10+
- PostgreSQL 13+
- Redis 6.0+
- Node.js 18+

### Backend Setup
1. Clone the repository and navigate to backend:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file in the backend directory (see `.env.example`):
   ```bash
   cp ../.env.example .env
   # Edit .env with your local database and Redis URLs
   ```

5. Run migrations and seed data:
   ```bash
   python manage.py migrate
   python manage.py seed_data
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

7. In separate terminals, start Celery worker and beat:
   ```bash
   celery -A payout_service worker --loglevel=info
   celery -A payout_service beat --loglevel=info
   ```

### Frontend Setup
1. Navigate to frontend:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

## Testing

### Run All Tests
```bash
cd backend
python manage.py test core.tests
```

### Test Concurrency
Tests simultaneous payout requests to ensure only one succeeds when balance is insufficient.

### Test Idempotency
Tests that duplicate requests with same Idempotency-Key return identical responses.

## Production Deployment

### Deploy to Render

1. Push to GitHub with `render.yaml` in root directory
2. Create new Web Service on Render pointing to this repo
3. Render will automatically:
   - Provision PostgreSQL database
   - Provision Redis instance
   - Run migrations on release
   - Seed initial data
   - Start web, worker, and beat services

### Deploy to Railway

1. Push to GitHub with `Procfile` in root directory
2. Create new project on Railway
3. Connect GitHub repo
4. Add PostgreSQL plugin
5. Add Redis plugin
6. Set environment variables (SECRET_KEY, DEBUG=False, etc.)
7. Deploy

### Deploy to Fly.io

Similar to Render - uses `Dockerfile` (not included, but can be generated)

### Required Environment Variables
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to False in production
- `DATABASE_URL`: PostgreSQL connection string
- `CELERY_BROKER_URL`: Redis URL
- `CELERY_RESULT_BACKEND`: Redis URL (same as broker)
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed origins

## API Endpoints

### Merchants
- `GET /api/merchants/` - List all merchants
- `GET /api/merchants/{id}/` - Get merchant details
- `GET /api/merchants/{id}/history/` - Get ledger history

### Payouts
- `POST /api/payouts/` - Create payout request
  - Header: `Idempotency-Key: <uuid>`
  - Body: `{"merchant_id": 1, "amount_paise": 5000, "bank_account_id": "..."}`

## Project Structure

```
.
├── backend/
│   ├── core/
│   │   ├── models.py          # Merchant, Payout, LedgerEntry, IdempotencyRecord
│   │   ├── views.py           # API endpoints with concurrency handling
│   │   ├── tasks.py           # Celery tasks for payout processing
│   │   ├── serializers.py     # DRF serializers
│   │   ├── tests.py           # Concurrency and idempotency tests
│   │   └── management/
│   │       └── commands/
│   │           └── seed_data.py
│   ├── payout_service/
│   │   ├── settings.py        # Django settings
│   │   ├── celery.py          # Celery configuration
│   │   ├── wsgi.py            # WSGI application
│   │   └── urls.py
│   ├── requirements.txt
│   └── manage.py
├── frontend/
│   ├── src/
│   │   └── App.jsx            # React dashboard
│   ├── package.json
│   └── tailwind.config.js
├── render.yaml                # Render deployment config
├── Procfile                   # Railway/Heroku config
└── README.md
```

## Key Technical Decisions

1. **Money as BigIntegerField**: No floats, always store paise as integers to avoid rounding errors.
2. **Database-Level Aggregation**: Balance is computed via DB SUM query, never Python arithmetic.
3. **Row-Level Locking**: `SELECT FOR UPDATE` ensures atomicity of balance check + debit.
4. **Idempotency Records**: Separate table to store responses, allowing safe retries without duplicate payouts.
5. **Ledger Table**: Double-entry inspired design with positive credits, negative debits, positive refunds.

See `EXPLAINER.md` for detailed technical explanations.

## Explainer
See [EXPLAINER.md](./backend/EXPLAINER.md) for technical deep-dives on concurrency, locking, and idempotency logic.
