#!/bin/bash

# Quick Deploy Script for Render.com

echo "🚀 AI Movie Recommender - Quick Deploy to Render.com"
echo "=================================================="
echo ""

echo "📋 Prerequisites:"
echo "✅ GitHub repository pushed"
echo "✅ render.yaml configuration ready"
echo "✅ requirements.txt present"
echo ""

echo "🔗 Manual Steps (5 minutes):"
echo "1. Go to https://render.com"
echo "2. Sign up with GitHub"
echo "3. Click 'New +' → 'Web Service'"
echo "4. Connect repo: faizanshoukat5/AI-Movie-Recommender"
echo "5. Use these settings:"
echo "   - Name: ai-movie-backend"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: python app.py"
echo "   - Plan: Free"
echo ""

echo "🌐 After deployment:"
echo "1. Copy your backend URL (e.g., https://ai-movie-backend-xxx.onrender.com)"
echo "2. Update frontend API_BASE_URL"
echo "3. Redeploy frontend to Firebase"
echo ""

echo "💡 Pro tip: Use render.yaml for automatic configuration!"
echo ""

read -p "Press Enter to continue to GitHub repository..."
echo "Opening GitHub repo..."

# Commit and push latest changes
git add .
git commit -m "🚀 Added Render.com deployment configuration

- Updated render.yaml for free tier deployment
- Added comprehensive deployment guide
- Ready for one-click Render deployment"

git push origin main

echo "✅ Latest changes pushed to GitHub!"
echo "🔗 Repository: https://github.com/faizanshoukat5/AI-Movie-Recommender"
echo ""
echo "Next: Go to render.com and deploy! 🚀"
