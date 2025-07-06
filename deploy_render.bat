@echo off
cls

echo ========================================
echo   AI Movie Recommender - Quick Deploy  
echo ========================================
echo.

echo 🚀 Deploy Backend to Render.com (FREE)
echo.

echo 📋 What you need:
echo ✅ GitHub account
echo ✅ 5 minutes of time
echo.

echo 🔗 Quick Steps:
echo 1. Go to https://render.com
echo 2. Sign up with GitHub
echo 3. Click "New +" then "Web Service"
echo 4. Connect repo: faizanshoukat5/AI-Movie-Recommender  
echo 5. Configure:
echo    - Name: ai-movie-backend
echo    - Build: pip install -r requirements.txt
echo    - Start: python app.py
echo    - Plan: FREE
echo.

echo 💡 Benefits of Render:
echo ✅ 100%% FREE (750 hours/month)
echo ✅ Auto-deploy from GitHub
echo ✅ HTTPS included
echo ✅ No credit card needed
echo.

echo ⚠️  Note: App sleeps after 15 min inactivity
echo    (wakes up in ~30 seconds when accessed)
echo.

pause

echo.
echo 📤 Pushing latest changes to GitHub...

git add .
git commit -m "🚀 Final deployment configuration for Render.com - Ready to deploy backend for FREE!"
git push origin main

echo.
echo ✅ Repository updated!
echo 🔗 GitHub: https://github.com/faizanshoukat5/AI-Movie-Recommender
echo.
echo 🌐 Frontend already live: https://ai-movie-recommendation-engine.web.app
echo.
echo 👆 Now go to render.com and deploy the backend!
echo    Your full-stack app will be 100%% functional and FREE!
echo.

pause
