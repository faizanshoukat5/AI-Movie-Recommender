# 🆓 FREE Backend Deployment - Final Instructions

## 🎯 RECOMMENDED: Render.com (100% FREE)

### ⚡ Quick 5-Minute Setup:

1. **Go to [render.com](https://render.com)**
2. **Sign up** with your GitHub account
3. **Click "New +"** → **"Web Service"**
4. **Connect repository:** `faizanshoukat5/AI-Movie-Recommender`
5. **Use these EXACT settings:**
   ```
   Name: ai-movie-backend
   Root Directory: (leave empty)
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python app.py
   Plan: Free
   ```

### 🔧 Environment Variables (Add in Render dashboard):
```
FLASK_ENV=production
PORT=10000
TMDB_API_KEY=89cf1a0e526c7c36bafe8d77248d276d
```

### ✅ Your backend will be live at:
`https://ai-movie-backend-[random].onrender.com`

---

## 🔄 Complete the Deployment:

### Step 1: Deploy Backend (5 minutes)
Follow Render.com steps above

### Step 2: Update Frontend (2 minutes)
1. Copy your backend URL from Render
2. Update `src/App.js` line 12:
   ```javascript
   const API_BASE_URL = 'https://your-backend-url.onrender.com';
   ```
3. Rebuild and redeploy:
   ```bash
   cd recommendation-frontend
   npm run build
   firebase deploy --only hosting
   ```

### 🎊 DONE! Full-stack app live and FREE!

---

## 🆓 Alternative Free Options:

### 2. Railway.app
- $5/month credit (usually enough)
- Always-on (doesn't sleep)
- Go to [railway.app](https://railway.app)
- "Deploy from GitHub repo"

### 3. PythonAnywhere
- 100% free tier
- Python-focused hosting
- Good for smaller Flask apps

### 4. Vercel (with some config)
- Free tier available
- Requires serverless function setup

---

## 💡 Why Render.com?
✅ **Completely FREE** (750 hours/month)
✅ **No credit card** required
✅ **Auto-deploy** from GitHub
✅ **HTTPS** included
✅ **Easy setup** (5 minutes)

⚠️ **Only downside:** Sleeps after 15 min (wakes in ~30 sec)

---

## 🚀 Your Current Status:
✅ **Frontend LIVE:** https://ai-movie-recommendation-engine.web.app
✅ **Backend ready** for deployment
✅ **All files** configured for free hosting
✅ **GitHub repo** up-to-date

**Next:** Deploy backend → Update API URL → Full-stack app LIVE! 🎉
