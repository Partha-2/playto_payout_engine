# Deployment Checklist

This document guides you through deploying Playto Payout Engine to production.

## Pre-Deployment

### Code Quality Checks
- [ ] Run tests: `python manage.py test core.tests`
- [ ] Check for migrations: `python manage.py makemigrations --dry-run`
- [ ] Verify no uncommitted changes: `git status`
- [ ] Review EXPLAINER.md for accuracy

### Local Testing
- [ ] Test with Docker Compose: `docker-compose up`
- [ ] Verify all API endpoints work
- [ ] Test concurrency scenario
- [ ] Test idempotency scenario

## Deploy to Render

### Step 1: Prepare Repository
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Create Render Service
1. Go to [render.com](https://render.com)
2. Click "New +" > "Web Service"
3. Connect your GitHub repository
4. Select the repo (playto_payout_engine)
5. Set build command: Use default or override with `cd backend && pip install -r requirements.txt`
6. Set start command: Use default from render.yaml

### Step 3: Environment Variables
Render will automatically generate SECRET_KEY. Verify these are set:
- `DEBUG=False`
- `ALLOWED_HOSTS=*.onrender.com,localhost`
- `DATABASE_URL` - auto-generated from postgres service
- `CELERY_BROKER_URL` - auto-generated from redis service
- `CELERY_RESULT_BACKEND` - auto-generated from redis service

### Step 4: Verify Deployment
```bash
# Check your deployment URL
https://your-service-name.onrender.com/api/v1/merchants/

# Check background worker is running
# Monitor logs in Render dashboard
```

## Deploy to Railway

### Step 1: Prepare Repository
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Create Railway Project
1. Go to [railway.app](https://railway.app)
2. Click "New Project" > "Deploy from GitHub"
3. Select your repository
4. Configure services:
   - PostgreSQL plugin
   - Redis plugin

### Step 3: Set Environment Variables
In Railway dashboard, set:
- `SECRET_KEY` - generate: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
- `DEBUG=False`
- `DATABASE_URL` - Railway will auto-populate
- `CELERY_BROKER_URL` - Railway Redis URL
- `CELERY_RESULT_BACKEND` - Railway Redis URL

### Step 4: Deploy
Railway automatically deploys on push to main branch.

## Post-Deployment

### Verify Everything Works
```bash
# 1. Check API is accessible
curl https://your-deployment-url/api/v1/merchants/

# 2. Verify merchants were seeded
curl https://your-deployment-url/api/v1/merchants/

# 3. Try creating a payout
curl -X POST https://your-deployment-url/api/v1/payouts \
  -H "Idempotency-Key: $(uuidgen)" \
  -H "Content-Type: application/json" \
  -d '{"merchant_id": 1, "amount_paise": 5000, "bank_account_id": "TEST-123"}'

# 4. Check background worker is processing payouts
# Look at logs for "processing payout"
```

### Monitor Production
- Watch logs for errors
- Monitor Celery task queue
- Set up error tracking (Sentry recommended)
- Track database connections

## Troubleshooting

### psycopg2 Build Error
**Problem:** "Error loading psycopg2 or psycopg module"

**Solution:** 
- We've switched to `psycopg2` (instead of binary)
- Added proper connection handling via `dj-database-url`
- If still fails, Render may need build cache cleared

**Clear Cache on Render:**
1. Go to Settings > Build & Deploy
2. Click "Clear Build Cache"
3. Redeploy

### Migrations Not Running
**Problem:** "Table core_merchant does not exist"

**Solution:**
- Verify release command runs: `python manage.py migrate`
- Check logs: `heroku logs --app your-app` (or Render equivalent)
- Manual fix: Run `python manage.py migrate` in production shell

### Celery Tasks Not Processing
**Problem:** Payouts stuck in PENDING status

**Solution:**
- Check Redis connection: `redis-cli -u $REDIS_URL PING`
- Verify worker is running: Check logs for "celery worker started"
- Check for task errors: `celery -A payout_service inspect active`

### Static Files Not Loading (Frontend)
**Problem:** 404 on frontend CSS/JS

**Solution:**
- Frontend is separate service (Vite build)
- Can deploy to Vercel/Netlify separately
- Or run from same server but on different port

## Final Submission

Before submitting to Playto, ensure:

1. **GitHub repo is public** and clean
2. **Deployment URL works** - all endpoints respond
3. **EXPLAINER.md is complete** - all 5 sections fully explained
4. **Tests pass** - `python manage.py test core.tests`
5. **Data is seeded** - merchants have sample credit history
6. **No hardcoded secrets** - all in environment variables

### Submit Form
Fill out: https://forms.gle/71gdyG9KyvddrVu6

Include:
- GitHub repo URL
- Live deployment URL (Render, Railway, etc.)
- Brief note on what you're proud of
