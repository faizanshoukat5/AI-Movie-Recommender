@echo off
echo 🚀 AI Movie Recommender - Backend Deployment Script
echo ==================================================

echo.
echo 📋 Deployment Options:
echo 1. Deploy to Railway (railway.app)
echo 2. Deploy to Render (render.com) 
echo 3. Deploy to Heroku
echo 4. View deployment URLs
echo.

set /p choice="Choose deployment option (1-4): "

if "%choice%"=="1" (
    echo 🚂 Deploying to Railway...
    echo Please visit: https://railway.app
    echo 1. Login with GitHub
    echo 2. Click 'New Project' → 'Deploy from GitHub repo'
    echo 3. Select: AI-Movie-Recommender
    echo 4. Railway will auto-deploy using railway.json
)

if "%choice%"=="2" (
    echo 🎨 Deploying to Render...
    echo Please visit: https://render.com
    echo 1. Login with GitHub
    echo 2. Click 'New' → 'Web Service'
    echo 3. Connect: AI-Movie-Recommender repository
    echo 4. Use render.yaml configuration
)

if "%choice%"=="3" (
    echo 🟣 Deploying to Heroku...
    echo Please install Heroku CLI first if not installed
    echo Visit: https://devcenter.heroku.com/articles/heroku-cli
    echo Then run: heroku create your-app-name
    echo Then run: git push heroku main
)

if "%choice%"=="4" (
    echo 🌐 Common Deployment URLs:
    echo - Railway: https://your-app.railway.app
    echo - Render: https://your-app.onrender.com  
    echo - Heroku: https://your-app.herokuapp.com
)

echo.
echo 🔗 After backend deployment:
echo 1. Copy your backend URL
echo 2. Update API_BASE_URL in recommendation-frontend/src/App.js
echo 3. Run: npm run build ^&^& firebase deploy --only hosting
echo.
echo ✨ Your app will be fully functional!
pause
