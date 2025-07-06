@echo off
REM Production deployment script for AI Movie Recommendation Engine (Windows)
REM This script sets up the production environment and deploys the backend

echo === AI Movie Recommendation Engine - Production Deployment ===

REM Check if Python is available
python --version
if %errorlevel% neq 0 (
    echo Error: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install production dependencies
echo Installing production dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Install optional production dependencies
echo Installing optional production dependencies...
pip install gunicorn psycopg2-binary redis celery

REM Set environment variables for production
echo Setting up environment variables...
set FLASK_ENV=production
set FLASK_APP=app_production.py
set PORT=5000

REM Database configuration (uncomment for PostgreSQL)
REM set DB_HOST=localhost
REM set DB_PORT=5432
REM set DB_NAME=movie_recommendations
REM set DB_USER=postgres
REM set DB_PASSWORD=your_password

REM TMDB API configuration
if "%TMDB_API_KEY%"=="" (
    echo Warning: TMDB_API_KEY not set. Movie posters may not work properly.
)

REM Firebase configuration
if not exist "firebase-service-account.json" (
    echo Warning: firebase-service-account.json not found. Firebase integration will be disabled.
)

REM Create logs directory
if not exist "logs" mkdir logs

REM Run database migrations/setup
echo Setting up database...
python -c "from production_rating_db import ProductionRatingDatabase; db = ProductionRatingDatabase(); print('Database setup complete')"

REM Test the application
echo Testing application...
python -c "import sys; sys.path.append('.'); from app_production import app; client = app.test_client(); response = client.get('/health'); print('✓ Health check passed' if response.status_code == 200 else '✗ Health check failed'); sys.exit(0 if response.status_code == 200 else 1)"

if %errorlevel% neq 0 (
    echo Application test failed. Check the logs.
    pause
    exit /b 1
)

REM Start the production server
echo Starting production server...
echo Access the API at: http://localhost:%PORT%
echo Health check: http://localhost:%PORT%/health
echo API documentation: http://localhost:%PORT%/

REM Use Gunicorn for production (if available)
where gunicorn >nul 2>nul
if %errorlevel% equ 0 (
    echo Starting with Gunicorn (production WSGI server)...
    gunicorn --bind 0.0.0.0:%PORT% --workers 4 --timeout 120 --log-level info --access-logfile logs/access.log --error-logfile logs/error.log app_production:app
) else (
    echo Gunicorn not found. Starting with Flask development server...
    python app_production.py
)

pause
