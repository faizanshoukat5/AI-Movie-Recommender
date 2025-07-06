# Render.com Deployment Configuration

## Flask Backend on Render.com (FREE)

### Step-by-Step Deployment:

1. **Go to [render.com](https://render.com)**
2. **Sign up** with your GitHub account
3. **Click "New +"** → **"Web Service"**
4. **Connect your GitHub repo:** `faizanshoukat5/AI-Movie-Recommender`
5. **Configure:**
   - **Name:** `ai-movie-backend`
   - **Root Directory:** `.` (leave empty)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
   - **Plan:** `Free`

### Environment Variables:
Add these in Render dashboard:
```
FLASK_ENV=production
PORT=10000
```

### Your app will be live at:
`https://ai-movie-backend-[random].onrender.com`

### Pros of Render:
✅ **Always free** (750 hours/month)
✅ **Auto-deploy** from GitHub
✅ **HTTPS included**
✅ **No credit card** required
✅ **Easy setup** (5 minutes)

### Cons:
⚠️ **Sleeps after 15 min** of inactivity
⚠️ **Cold start** ~30 seconds wake time

---

## Alternative: Railway.app

If you prefer Railway:
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. "Deploy from GitHub repo"
4. Select your repo
5. Railway auto-detects Python and deploys

**Railway gives $5/month credit** which is usually enough for small apps.

---

## Post-Deployment Steps:

Once backend is deployed, update your React app:

1. **Update API_BASE_URL** in `src/App.js`:
```javascript
const API_BASE_URL = 'https://your-backend-url.onrender.com';
```

2. **Rebuild and redeploy frontend:**
```bash
cd recommendation-frontend
npm run build
firebase deploy --only hosting
```

Your full-stack app will then be **100% live and functional!**
