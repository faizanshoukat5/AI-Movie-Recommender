# 🚀 One-Click Backend Deployment

## Quick Deploy Links

### Railway (Recommended - Free Tier Available)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/jW7FfM?referralCode=alphasec)

**Manual Railway Deployment:**
1. Visit [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Choose `AI-Movie-Recommender`
5. Railway automatically detects Python and deploys!

### Render (Free Tier Available)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

**Manual Render Deployment:**
1. Visit [render.com](https://render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository: `AI-Movie-Recommender`
4. Render will use the `render.yaml` configuration

### Heroku (Free Tier Discontinued - Paid Only)
```bash
heroku create ai-movie-recommender-api
git push heroku main
```

## After Deployment

1. **Copy your backend URL** (e.g., `https://ai-movie-recommender-api.railway.app`)
2. **Update the frontend** to use the new backend URL
3. **Redeploy frontend** with updated API URL

## Environment Variables
The following are automatically configured:
- `TMDB_API_KEY`: Pre-configured for movie posters
- `FLASK_ENV`: Set to production
- `PORT`: Automatically set by hosting platform
