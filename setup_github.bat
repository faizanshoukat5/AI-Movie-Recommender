@echo off
REM Quick GitHub setup script for AI Movie Recommendation Engine (Windows)

echo 🚀 Setting up GitHub deployment for AI Movie Recommendation Engine
echo ============================================================

REM Check if git is initialized
if not exist ".git" (
    echo 📁 Initializing Git repository...
    git init
) else (
    echo ✅ Git repository already exists
)

REM Add all files
echo 📦 Adding files to Git...
git add .

REM Commit changes
echo 💾 Committing changes...
git commit -m "Production-ready backend with PythonAnywhere optimization" -m "Features:" -m "- Production-optimized Flask backend (app_pythonanywhere.py)" -m "- PythonAnywhere-specific configuration" -m "- Enhanced database with PostgreSQL support" -m "- Intelligent caching system" -m "- Comprehensive error handling" -m "- Health monitoring endpoints" -m "- Firebase integration" -m "- TMDB API integration" -m "- Complete deployment documentation"

echo ✅ Repository ready for GitHub!
echo.
echo 🔗 Next steps:
echo 1. Create a new repository on GitHub.com
echo 2. Copy these commands to push your code:
echo.
echo git remote add origin https://github.com/yourusername/ai-movie-recommendation-engine.git
echo git branch -M main
echo git push -u origin main
echo.
echo 3. Then clone on PythonAnywhere:
echo git clone https://github.com/yourusername/ai-movie-recommendation-engine.git mysite
echo.
echo 🎉 Much easier than manual uploads!

pause
