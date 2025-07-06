@echo off
echo ====================================
echo   AI Movie Recommendation Engine
echo   Firebase Deployment Script
echo ====================================
echo.

echo Building React frontend...
cd recommendation-frontend
call npm run build
cd ..

echo.
echo Deploying to Firebase...
call firebase deploy --only hosting

echo.
echo ====================================
echo   Deployment Complete!
echo   Your app is live at:
echo   https://ai-movie-recommendation-engine.web.app
echo ====================================
pause
