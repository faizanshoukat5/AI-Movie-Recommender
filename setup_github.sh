#!/bin/bash
# Quick GitHub setup script for AI Movie Recommendation Engine

echo "🚀 Setting up GitHub deployment for AI Movie Recommendation Engine"
echo "=" * 60

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
else
    echo "✅ Git repository already exists"
fi

# Add all files
echo "📦 Adding files to Git..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "Production-ready backend with PythonAnywhere optimization

Features:
- Production-optimized Flask backend (app_pythonanywhere.py)
- PythonAnywhere-specific configuration
- Enhanced database with PostgreSQL support
- Intelligent caching system
- Comprehensive error handling
- Health monitoring endpoints
- Firebase integration
- TMDB API integration
- Complete deployment documentation"

echo "✅ Repository ready for GitHub!"
echo ""
echo "🔗 Next steps:"
echo "1. Create a new repository on GitHub.com"
echo "2. Copy these commands to push your code:"
echo ""
echo "git remote add origin https://github.com/yourusername/ai-movie-recommendation-engine.git"
echo "git branch -M main"
echo "git push -u origin main"
echo ""
echo "3. Then clone on PythonAnywhere:"
echo "git clone https://github.com/yourusername/ai-movie-recommendation-engine.git mysite"
echo ""
echo "🎉 Much easier than manual uploads!"
