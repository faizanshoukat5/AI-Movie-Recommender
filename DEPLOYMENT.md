# 🚀 Backend Deployment Guide

## Quick Deploy Options

### Option 1: Railway (Recommended)
1. Go to [railway.app](https://railway.app)
2. Sign up/Login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `AI-Movie-Recommender` repository
5. Railway will auto-detect Python and deploy using the Procfile
6. Your backend will be live at: `https://your-app-name.railway.app`

### Option 2: Render
1. Go to [render.com](https://render.com)
2. Sign up/Login with GitHub
3. Click "New" → "Web Service"
4. Connect your `AI-Movie-Recommender` repository
5. Use these settings:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
6. Your backend will be live at: `https://your-app-name.onrender.com`

### Option 3: Heroku
1. Install Heroku CLI
2. Run: `heroku create your-app-name`
3. Run: `git push heroku main`
4. Your backend will be live at: `https://your-app-name.herokuapp.com`

## After Backend Deployment

1. Copy your backend URL (e.g., `https://your-app-name.railway.app`)
2. Update `API_BASE_URL` in `recommendation-frontend/src/App.js`
3. Rebuild and redeploy frontend:
   ```bash
   cd recommendation-frontend
   npm run build
   firebase deploy --only hosting
   ```

## Environment Variables Needed
- `TMDB_API_KEY`: Your TMDB API key
- `FLASK_ENV`: Set to "production" for production deployment
