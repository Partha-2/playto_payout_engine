# Pre-Submission Checklist

Use this checklist to verify everything is ready before submitting to Playto.

## Code Quality

- [x] All Python files follow PEP 8
- [x] No hardcoded secrets or credentials
- [x] All sensitive config uses environment variables
- [x] No TODO comments left in critical code
- [x] Import statements are organized
- [x] Docstrings for key functions

## Functionality

- [x] Ledger model stores amounts as BigIntegerField (paise)
- [x] Balance calculated via DB aggregation (SELECT ... SUM)
- [x] No FloatField or DecimalField for money
- [x] Payout API at POST /api/v1/payouts
- [x] Idempotency-Key header required
- [x] Request returns same response for duplicate keys
- [x] Merchant dashboard shows available balance
- [x] Dashboard shows held (PENDING/PROCESSING) balance
- [x] Dashboard shows recent payout history
- [x] Dashboard shows ledger activity
- [x] Form to request payouts on dashboard
- [x] Live status updates for payouts

## Concurrency & Data Integrity

- [x] SELECT FOR UPDATE locks merchant during balance check
- [x] Two concurrent requests can't both overdraw balance
- [x] Race condition test passes
- [x] Payout debit and status change are atomic
- [x] Refund and state change are atomic on failure
- [x] unique_together constraints on (merchant, idempotency_key)
- [x] Database maintains invariant: Sum(credits - debits) = balance

## Idempotency

- [x] IdempotencyRecord table stores request/response
- [x] Keys scoped to merchant
- [x] Second identical request returns exact same response
- [x] No duplicate payout created on duplicate request
- [x] Test for idempotency passes
- [x] In-flight handling via unique constraint

## State Machine

- [x] Legal transitions: PENDING → PROCESSING → COMPLETED
- [x] Legal transitions: PENDING → PROCESSING → FAILED
- [x] Illegal transitions rejected (COMPLETED → PENDING, etc.)
- [x] Failed → PENDING blocked
- [x] COMPLETED status cannot change
- [x] Failed payout returns funds atomically
- [x] Retry logic for stuck payouts (> 30s)
- [x] Max 3 retries before marking failed

## Background Processing

- [x] Celery worker processes payout tasks
- [x] Simulation: 70% success, 20% fail, 10% hang
- [x] Successful payout: status → COMPLETED
- [x] Failed payout: status → FAILED, funds refunded
- [x] Hung payouts detected and retried
- [x] Celery beat scheduled for payout watcher
- [x] Stuck payout watcher runs every 10 seconds
- [x] Exponential backoff on retries

## Seeding & Initial Data

- [x] Seed script creates 2-3 merchants
- [x] Merchants have credit history (simulated customer payments)
- [x] Seeds run automatically on deployment
- [x] Balances are realistic (thousands of paise)
- [x] Can be run multiple times safely

## Testing

- [x] Concurrency test exists and passes
- [x] Idempotency test exists and passes
- [x] Tests use TransactionTestCase for atomicity
- [x] Tests verify database invariants
- [x] Tests can be run locally: `python manage.py test core.tests`

## Documentation

- [x] README.md with setup instructions
- [x] README.md with deployment instructions
- [x] EXPLAINER.md section 1: The Ledger (balance query + why)
- [x] EXPLAINER.md section 2: The Lock (SELECT FOR UPDATE code + explanation)
- [x] EXPLAINER.md section 3: The Idempotency (how system tracks keys + in-flight handling)
- [x] EXPLAINER.md section 4: The State Machine (where illegal transitions blocked)
- [x] EXPLAINER.md section 5: The AI Audit (specific AI bug + your fix)
- [x] QUICKSTART.md for quick local setup
- [x] DEPLOYMENT.md for production deployment
- [x] .env.example template

## Infrastructure

- [x] render.yaml configured for Render deployment
- [x] Procfile for Railway/Heroku
- [x] docker-compose.yml for local development
- [x] Dockerfile.dev for backend container
- [x] Dockerfile.frontend for frontend container
- [x] PostgreSQL support (both SQLite for dev, Postgres for prod)
- [x] Redis configured for Celery
- [x] Environment variables properly configured
- [x] SECRET_KEY can be set via environment
- [x] DEBUG mode can be set via environment

## Dependencies

- [x] requirements.txt has all backend dependencies
- [x] psycopg2 (not binary) for PostgreSQL
- [x] dj-database-url for connection strings
- [x] django-celery-beat for scheduler
- [x] whitenoise for static files
- [x] All dependencies pinned to specific versions
- [x] package.json has all frontend dependencies
- [x] Node dependencies include axios, react, tailwindcss, framer-motion

## Frontend

- [x] React app shows merchant dashboard
- [x] Displays available balance in rupees
- [x] Displays held balance (PENDING + PROCESSING)
- [x] Shows recent payouts with status
- [x] Shows ledger history
- [x] Form to request payout
- [x] Amount input validation
- [x] Bank account selection
- [x] Sends Idempotency-Key header
- [x] Shows error messages
- [x] Shows loading states
- [x] Live polling for updates (5 second interval)
- [x] Uses Tailwind CSS
- [x] Uses Framer Motion for animations
- [x] Responsive design
- [x] Dark theme
- [x] Environment-based API URL (VITE_API_URL)

## Deployment Readiness

- [x] No hardcoded localhost URLs
- [x] API base URL configurable
- [x] Database URL from environment
- [x] Redis URL from environment
- [x] SECRET_KEY from environment
- [x] DEBUG=False in production
- [x] Migrations run automatically
- [x] Seeds data automatically on deployment
- [x] Static files collected/served properly
- [x] CORS configured for frontend access
- [x] ALLOWED_HOSTS includes deployment domain
- [x] Connection pooling configured for PostgreSQL

## Git Repository

- [x] Clean git history (no merge commits for simple changes)
- [x] Meaningful commit messages
- [x] All necessary files committed
- [x] .gitignore prevents committing secrets/venv/node_modules
- [x] No build artifacts committed
- [x] README visible on GitHub homepage
- [x] Can clone and run immediately

## Before Final Submission

- [ ] Test locally with docker-compose:
  ```bash
  docker-compose up
  docker-compose exec backend python manage.py seed_data
  ```

- [ ] Verify all endpoints work:
  ```bash
  curl http://localhost:8000/api/v1/merchants/
  ```

- [ ] Run tests:
  ```bash
  cd backend
  python manage.py test core.tests -v 2
  ```

- [ ] Frontend loads and can create payouts:
  ```
  Open http://localhost:5173 in browser
  Try creating a payout
  Watch status change as Celery processes it
  ```

- [ ] Deploy to Render or Railway (test deployment):
  - Push to GitHub
  - Create new deployment on Render/Railway
  - Verify migrations run successfully
  - Verify seeds created merchants
  - Test live API endpoint
  - Record deployment URL

- [ ] Final checks:
  - [ ] GitHub repo URL is correct
  - [ ] Deployment URL is correct and working
  - [ ] All endpoints respond
  - [ ] Dashboard loads
  - [ ] Create payout works
  - [ ] EXPLAINER.md is complete and accurate
  - [ ] No console errors or warnings
  - [ ] Database integrity verified
  - [ ] Celery tasks processing

## Submission

When ready, fill out: https://forms.gle/71gdyG9KyvddrVu6

**Form requires:**
1. GitHub repo URL: https://github.com/Partha-2/playto_payout_engine
2. Live deployment URL: https://your-deployment.onrender.com
3. Brief note on what you're proud of:
   - Example: "I'm proud of the concurrency handling with SELECT FOR UPDATE and the thorough testing for edge cases"
   - Focus on technical decisions, not UI

## Common Issues & Fixes

### Build Error: psycopg2 not found
- Already fixed: using psycopg2 instead of binary
- If still fails: clear cache on Render

### Tests fail to find endpoints
- Ensure settings.py has DEBUG settings
- Check BASE_DIR paths are correct
- Run migrations first

### Payouts stuck in PENDING
- Verify Redis is running
- Check Celery worker logs
- Verify environment variables for CELERY_BROKER_URL

### API CORS errors
- Check CORS_ALLOWED_ORIGINS setting
- Should include frontend domain
- Check in production it matches deployment domain

### Frontend can't reach API
- Check VITE_API_URL environment variable
- Ensure API is accessible from frontend domain
- Check browser console for actual URL being used

## Success Criteria

You know you're ready when:

1. ✅ All 5 tests pass without errors
2. ✅ docker-compose up works perfectly
3. ✅ Local frontend can create payouts
4. ✅ Payouts move through state transitions
5. ✅ Concurrent requests handled correctly
6. ✅ Deployment to Render/Railway succeeds
7. ✅ Live API endpoints work
8. ✅ No hardcoded secrets in code
9. ✅ EXPLAINER.md is comprehensive
10. ✅ All files are committed to GitHub

## Final Reminder

This is a critical filter before CTO/CEO conversations. The evaluation is based on:

1. **Architecture** - How you model money and state
2. **Correctness** - Concurrency, idempotency, state machines work
3. **Understanding** - Your EXPLAINER.md shows you understand every line
4. **Production-readiness** - Code that could actually go live
5. **Honest AI audit** - Shows you caught AI mistakes

Focus on depth over breadth. Better to have 3 perfect features than 10 mediocre ones.

Good luck! 🚀
