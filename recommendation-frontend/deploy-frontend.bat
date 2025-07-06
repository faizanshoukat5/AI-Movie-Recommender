@echo off
echo 🚀 Frontend Deployment Script

REM Check if we're in the right directory
if not exist "package.json" (
    echo ❌ Error: package.json not found. Are you in the recommendation-frontend directory?
    echo Please run: cd recommendation-frontend
    pause
    exit /b 1
)

REM Prompt for backend URL
echo.
echo 📍 Enter your backend URL (e.g., https://yourusername.pythonanywhere.com):
set /p BACKEND_URL="Backend URL: "

if "%BACKEND_URL%"=="" (
    echo ❌ Error: Backend URL is required
    pause
    exit /b 1
)

REM Update production environment file
echo 🔧 Updating production environment...
echo REACT_APP_API_URL=%BACKEND_URL% > .env.production

REM Build the project
echo 🏗️ Building React app...
npm run build

if %errorlevel% neq 0 (
    echo ❌ Build failed
    pause
    exit /b 1
)

echo ✅ Build successful!

REM Deploy to Firebase
echo 🚀 Deploying to Firebase Hosting...
firebase deploy --only hosting

if %errorlevel% neq 0 (
    echo ❌ Firebase deployment failed
    pause
    exit /b 1
)

echo.
echo 🎉 Deployment Complete!
echo 📱 Frontend: https://ai-movie-recommendation-engine.web.app
echo 🖥️  Backend: %BACKEND_URL%
echo.
echo ✅ Your AI Movie Recommendation Engine is now live!
pause
