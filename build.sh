#!/bin/bash
set -e

echo "Building Playto Payout Engine..."

# Upgrade pip, setuptools, and wheel
pip install --upgrade pip setuptools wheel

# Install Python dependencies
cd backend
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate

echo "Seeding data..."
python manage.py seed_data

echo "Build completed successfully!"
