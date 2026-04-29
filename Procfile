release: cd backend && python manage.py migrate ; python manage.py seed_data ; echo "Migrations and seeding complete"
web: cd backend && gunicorn payout_service.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120
worker: cd backend && celery -A payout_service worker --loglevel=info
beat: cd backend && celery -A payout_service beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
