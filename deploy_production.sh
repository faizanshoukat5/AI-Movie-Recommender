#!/bin/bash

# Production deployment script for AI Movie Recommendation Engine
# This script sets up the production environment and deploys the backend

echo "=== AI Movie Recommendation Engine - Production Deployment ==="

# Check if Python 3.8+ is available
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install production dependencies
echo "Installing production dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install optional production dependencies
echo "Installing optional production dependencies..."
pip install gunicorn psycopg2-binary redis celery

# Set environment variables for production
echo "Setting up environment variables..."
export FLASK_ENV=production
export FLASK_APP=app_production.py
export PORT=5000

# Database configuration (uncomment for PostgreSQL)
# export DB_HOST=localhost
# export DB_PORT=5432
# export DB_NAME=movie_recommendations
# export DB_USER=postgres
# export DB_PASSWORD=your_password

# TMDB API configuration
if [ -z "$TMDB_API_KEY" ]; then
    echo "Warning: TMDB_API_KEY not set. Movie posters may not work properly."
fi

# Firebase configuration
if [ ! -f "firebase-service-account.json" ]; then
    echo "Warning: firebase-service-account.json not found. Firebase integration will be disabled."
fi

# Create logs directory
mkdir -p logs

# Run database migrations/setup
echo "Setting up database..."
python3 -c "
from production_rating_db import ProductionRatingDatabase
db = ProductionRatingDatabase()
print('Database setup complete')
"

# Test the application
echo "Testing application..."
python3 -c "
import sys
sys.path.append('.')
from app_production import app
with app.test_client() as client:
    response = client.get('/health')
    if response.status_code == 200:
        print('✓ Health check passed')
    else:
        print('✗ Health check failed')
        sys.exit(1)
"

# Start the production server
echo "Starting production server..."
echo "Access the API at: http://localhost:$PORT"
echo "Health check: http://localhost:$PORT/health"
echo "API documentation: http://localhost:$PORT/"

# Use Gunicorn for production
if command -v gunicorn &> /dev/null; then
    echo "Starting with Gunicorn (production WSGI server)..."
    gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --log-level info --access-logfile logs/access.log --error-logfile logs/error.log app_production:app
else
    echo "Gunicorn not found. Starting with Flask development server..."
    python3 app_production.py
fi
