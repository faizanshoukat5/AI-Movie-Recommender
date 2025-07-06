@echo off
echo 🎬 AI Recommendation Engine Startup Script
echo ========================================
echo.

echo 📦 Starting Flask API Server...
cd /d "%~dp0"
start "Flask API Server" cmd /k "py app.py"

echo ⏳ Waiting for Flask API to initialize...
timeout /t 5 /nobreak >nul

echo 🚀 Starting React Frontend...
cd /d "%~dp0recommendation-frontend"
start "React Frontend" cmd /k "npm start"

echo.
echo ✅ Both servers are starting up!
echo.
echo 🌐 Access the application at:
echo   - Flask API: http://localhost:5000
echo   - React Frontend: http://localhost:3001
echo.
echo 📚 API Documentation: http://localhost:5000/health
echo.
echo Press any key to exit this script...
pause >nul
