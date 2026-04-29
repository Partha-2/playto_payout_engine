# 🚀 IMMEDIATE ACTION PLAN - Deploy in Next 1-2 Hours

This is your quick action plan to get the project deployed today.

## What's Already Done ✅

- ✅ Backend API fully functional (models, views, serializers)
- ✅ Concurrency handling with SELECT FOR UPDATE
- ✅ Idempotency with unique constraints
- ✅ Background task processing with Celery
- ✅ React frontend with live updates
- ✅ All tests passing locally
- ✅ Deployment configs created (render.yaml, Procfile)
- ✅ Docker setup for local testing
- ✅ Comprehensive documentation
- ✅ Fixed psycopg2 issue

## What You Need to Do Now (In Order)

### STEP 1: Test Locally (15 minutes) 

**Goal**: Verify everything works before pushing to GitHub

```bash
# Navigate to project
cd backend

# Test API runs
python manage.py migrate
python manage.py seed_data
python manage.py test core.tests

# Expected output: 2 tests passed
```

**If tests fail:**
- Check PostgreSQL is running: `psql --version`
- Check Redis is running: `redis-cli ping`
- Delete old database: `rm db.sqlite3`
- Re-run migrations

### STEP 2: Test with Docker (10 minutes)

**Goal**: Verify Docker setup works (closer to production)

```bash
# From project root
docker-compose up

# In another terminal
docker-compose exec backend python manage.py seed_data

# Verify
curl http://localhost:8000/api/v1/merchants/

# Expected: JSON list of merchants
```

**If Docker fails:**
- Check Docker is running: `docker ps`
- Rebuild: `docker-compose down && docker-compose build --no-cache`
- Check logs: `docker-compose logs -f backend`

### STEP 3: Push to GitHub (5 minutes)

```bash
# Check what's new
git status

# Add all changes
git add .

# Commit with meaningful message
git commit -m "Deployment ready: fixed psycopg2, added render.yaml, docker-compose, updated settings"

# Push to main
git push origin main

# Verify on GitHub (refresh page)
# Should see all new files
```

### STEP 4: Deploy to Render (20 minutes)

**Option A: Automatic via GitHub**

1. Go to **render.com**
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect to GitHub"**
4. Search for `playto_payout_engine`
5. Select repository
6. **Important**: Leave all settings as default (Render will read render.yaml)
7. Click **"Deploy"**

**Wait for build to complete** (usually 2-3 minutes)

**Option B: If render.yaml not auto-detected**

1. Go to Render dashboard
2. Click deployed service
3. Go to **Settings** → **Build & Deploy**
4. Change "Build Command" to:
   ```
   cd backend && pip install -r requirements.txt && python manage.py migrate && python manage.py seed_data
   ```
5. Change "Start Command" to:
   ```
   cd backend && gunicorn payout_service.wsgi:application --bind 0.0.0.0:$PORT
   ```
6. Click **"Save"** → **"Deploy"**

### STEP 5: Verify Deployment (5 minutes)

After deployment completes:

```bash
# Get your Render URL (format: https://playto-payout-engine.onrender.com)
# Replace URL below with your actual Render URL

# Test 1: Check merchants
curl https://YOUR_RENDER_URL/api/v1/merchants/

# Expected: [{"id": 1, "name": "Alice Agencies", ...}, ...]

# Test 2: Check specific merchant
curl https://YOUR_RENDER_URL/api/v1/merchants/1/

# Test 3: Try creating a payout
curl -X POST https://YOUR_RENDER_URL/api/v1/payouts \
  -H "Idempotency-Key: 12345678-1234-1234-1234-123456789012" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_id": 1,
    "amount_paise": 5000,
    "bank_account_id": "TEST-BANK"
  }'

# Expected: {"id": 1, "status": "PENDING", ...}
```

### STEP 6: Check Backend Logs (2 minutes)

In Render dashboard:
1. Click your service
2. Go to **Logs** tab
3. Look for:
   - "migration applied" (migrations ran)
   - "Created merchant" (seed data created)
   - "Worker started" (celery running)
4. If errors, click **"Clear Build Cache"** and **"Redeploy"**

### STEP 7: Submit to Playto (5 minutes)

Fill out: **https://forms.gle/71gdyG9KyvddrVu6**

**Form fields:**
1. **GitHub Repo**: `https://github.com/Partha-2/playto_payout_engine`
2. **Live URL**: `https://your-render-url.onrender.com` (copy from Render)
3. **What I'm proud of**: Write 2-3 sentences about:
   - "Implemented robust concurrency handling with PostgreSQL locks, preventing race conditions on double-spend scenarios"
   - "Built complete idempotency system with response caching, ensuring safe retries"
   - "Created production-ready deployment with automated migrations and seed data"

## Troubleshooting (If Something Breaks)

### Deployment Stuck on "Building"
- Click **"Clear Build Cache"** in Settings
- Click **"Redeploy"**
- Wait 5 minutes

### "Error loading psycopg2" on Render
- This should be fixed (we use non-binary version)
- If still fails: clear cache and redeploy

### Migrations not running
- Go to Render dashboard
- Click **"Run Command"** button
- Paste: `cd backend && python manage.py migrate && python manage.py seed_data`
- Click **Run**

### Can't reach API endpoint
- Check URL format: `https://service-name.onrender.com/api/v1/...`
- Wait 2 minutes (may need to wake up free tier)
- Check logs for errors

### Payout stuck in PENDING
- This is OK! Background worker processes asynchronously
- Wait 30-60 seconds and check again
- If still stuck after 5 minutes: worker may not be running

## Success Criteria

You're done when:

✅ GitHub has all new files  
✅ Render deployment succeeds  
✅ `/api/v1/merchants/` returns data  
✅ Payout creation returns 201 status  
✅ Form submitted to Playto

## Timeline

- **Now**: Steps 1-2 (25 minutes)
- **In 30 minutes**: GitHub push (Step 3)
- **In 35 minutes**: Render deployment starts (Step 4)
- **In 60 minutes**: Verify deployment works (Step 5)
- **In 65 minutes**: Submit form (Step 7)

**Total time: ~1.5-2 hours from now**

## Final Reminder

- You have 5 days from task receipt
- Early submission shows confidence
- Live working code > perfect polish
- Every line of code should show you understand it

## Still Stuck?

1. Check QUICKSTART.md for local setup issues
2. Check DEPLOYMENT.md for deployment questions
3. Review EXPLAINER.md to ensure you understand your own code
4. Check project logs in Render dashboard

---

**GO GO GO! 🚀**

You're almost there. This is the final push.
