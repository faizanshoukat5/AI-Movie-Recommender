# 🚀 Final Deployment Guide: Backend + Frontend

## Current Status:
- ✅ **Frontend:** Live at https://ai-movie-recommendation-engine.web.app
- ⏳ **Backend:** Ready for deployment
- 🎯 **Goal:** Deploy backend and connect everything

## 🎯 Quick Deploy Options (All FREE):

### Option 1: PythonAnywhere (Recommended - Most Reliable)
**Why PythonAnywhere?**
- ✅ Always online (no sleeping)
- ✅ 100% free forever
- ✅ Python-focused
- ✅ Great for Flask apps

**Deploy Steps:**
1. **Create Account:** Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. **Open Bash Console** and run:
   ```bash
   git clone https://github.com/faizanshoukat5/AI-Movie-Recommender.git
   cd AI-Movie-Recommender
   pip3.10 install --user -r requirements.txt
   ```
3. **Create Web App:** Web tab → Add new web app → Manual config → Python 3.10
4. **Configure WSGI:** Edit WSGI file, replace `yourusername` with your actual username:
   ```python
   import sys
   import os
   
   path = '/home/yourusername/AI-Movie-Recommender'
   if path not in sys.path:
       sys.path.append(path)
   
   os.environ['FLASK_ENV'] = 'production'
   os.environ['TMDB_API_KEY'] = '89cf1a0e526c7c36bafe8d77248d276d'
   
   from app import app as application
   ```
5. **Reload Web App**
6. **Backend URL:** `https://yourusername.pythonanywhere.com`

### Option 2: Render.com (Alternative)
**Why Render?**
- ✅ Modern platform
- ✅ Git-based deployment
- ⚠️ Sleeps after 15 minutes

**Deploy Steps:**
1. Go to [render.com](https://render.com)
2. Connect GitHub repository
3. Choose "Web Service"
4. Set:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
5. Add environment variable: `TMDB_API_KEY=89cf1a0e526c7c36bafe8d77248d276d`
6. Deploy

### Option 3: Railway (Alternative)
**Why Railway?**
- ✅ Very simple deployment
- ✅ Git-based
- ⚠️ Limited free tier

**Deploy Steps:**
1. Go to [railway.app](https://railway.app)
2. "Deploy from GitHub repo"
3. Select your repository
4. Railway auto-detects Flask app
5. Add environment variable: `TMDB_API_KEY=89cf1a0e526c7c36bafe8d77248d276d`

## 🔄 After Backend Deployment:

### Update Frontend API URL:
1. **Get your backend URL** (e.g., `https://yourusername.pythonanywhere.com`)
2. **Update frontend config:**
   ```bash
   cd recommendation-frontend/src
   # Edit App.js or create a config file
   ```

3. **Method 1: Direct Edit (Quick)**
   Edit `recommendation-frontend/src/App.js`:
   ```javascript
   // Replace this line:
   const API_BASE_URL = 'http://localhost:5000';
   
   // With your backend URL:
   const API_BASE_URL = 'https://yourusername.pythonanywhere.com';
   ```

4. **Method 2: Environment Variable (Better)**
   Create `recommendation-frontend/.env.production`:
   ```
   REACT_APP_API_URL=https://yourusername.pythonanywhere.com
   ```
   
   Then update `App.js`:
   ```javascript
   const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
   ```

5. **Rebuild and Deploy Frontend:**
   ```bash
   cd recommendation-frontend
   npm run build
   firebase deploy --only hosting
   ```

## 🎯 Complete Deployment Commands:

### For PythonAnywhere:
```bash
# In PythonAnywhere bash console:
git clone https://github.com/faizanshoukat5/AI-Movie-Recommender.git
cd AI-Movie-Recommender
pip3.10 install --user -r requirements.txt

# Then configure web app in Web tab
```

### For Frontend Update:
```bash
# In your local machine:
cd "d:\AI Recommendation Engine\recommendation-frontend"
# Edit src/App.js with your backend URL
npm run build
firebase deploy --only hosting
```

## 🔧 Testing Your Deployment:

1. **Test Backend:** Visit `https://yourusername.pythonanywhere.com/movies/random`
2. **Test Frontend:** Visit `https://ai-movie-recommendation-engine.web.app`
3. **Test Integration:** Try getting recommendations in the frontend

## 📊 Expected URLs:
- **Frontend:** https://ai-movie-recommendation-engine.web.app
- **Backend:** https://yourusername.pythonanywhere.com (replace with your username)

## 🎉 You're Done!
Your AI Movie Recommendation Engine will be fully deployed and accessible worldwide!

## 🆘 Troubleshooting:
- **CORS errors:** Backend includes CORS headers, should work
- **API not found:** Check backend URL in frontend
- **Movies not loading:** Verify TMDB API key is set
- **Deployment failed:** Check deployment logs in respective platform

## 💡 Next Steps (Optional):
- Set up custom domain
- Add user authentication
- Implement user rating storage
- Add more recommendation algorithms
- Monitor usage and performance
