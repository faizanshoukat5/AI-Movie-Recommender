#!/bin/bash

echo "🚀 AI Movie Recommender - Backend Deployment Script"
echo "=================================================="

# Check if git is clean
if [[ -n $(git status --porcelain) ]]; then
    echo "⚠️  Git working directory is not clean. Committing changes..."
    git add .
    git commit -m "Auto-commit before deployment"
    git push origin main
fi

echo ""
echo "📋 Deployment Options:"
echo "1. Deploy to Railway (railway.app)"
echo "2. Deploy to Render (render.com)"
echo "3. Deploy to Heroku"
echo "4. View deployment URLs"
echo ""

read -p "Choose deployment option (1-4): " choice

case $choice in
    1)
        echo "🚂 Deploying to Railway..."
        echo "Please visit: https://railway.app"
        echo "1. Login with GitHub"
        echo "2. Click 'New Project' → 'Deploy from GitHub repo'"
        echo "3. Select: AI-Movie-Recommender"
        echo "4. Railway will auto-deploy using railway.json"
        ;;
    2)
        echo "🎨 Deploying to Render..."
        echo "Please visit: https://render.com"
        echo "1. Login with GitHub"
        echo "2. Click 'New' → 'Web Service'"
        echo "3. Connect: AI-Movie-Recommender repository"
        echo "4. Use render.yaml configuration"
        ;;
    3)
        echo "🟣 Deploying to Heroku..."
        if command -v heroku &> /dev/null; then
            heroku create ai-movie-recommender-api-$(date +%s)
            git push heroku main
        else
            echo "Please install Heroku CLI first"
            echo "Visit: https://devcenter.heroku.com/articles/heroku-cli"
        fi
        ;;
    4)
        echo "🌐 Common Deployment URLs:"
        echo "- Railway: https://your-app.railway.app"
        echo "- Render: https://your-app.onrender.com"
        echo "- Heroku: https://your-app.herokuapp.com"
        ;;
    *)
        echo "Invalid option"
        ;;
esac

echo ""
echo "🔗 After backend deployment:"
echo "1. Copy your backend URL"
echo "2. Update API_BASE_URL in recommendation-frontend/src/App.js"
echo "3. Run: npm run build && firebase deploy --only hosting"
echo ""
echo "✨ Your app will be fully functional!"
