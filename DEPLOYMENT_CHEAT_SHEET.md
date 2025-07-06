# 🎯 DEPLOYMENT CHEAT SHEET

## Current Status:
✅ **Frontend:** https://ai-movie-recommendation-engine.web.app  
⏳ **Backend:** Ready to deploy  
🎯 **Goal:** Deploy backend and connect everything  

## 🚀 FASTEST DEPLOYMENT (5 minutes):

### Step 1: Deploy Backend (PythonAnywhere)
1. Go to **pythonanywhere.com** → Create free account
2. Open **Bash console** → Run:
   ```bash
   git clone https://github.com/faizanshoukat5/AI-Movie-Recommender.git
   cd AI-Movie-Recommender
   pip3.10 install --user -r requirements.txt
   ```
3. Go to **Web tab** → Add new web app → Manual config → Python 3.10
4. Click **WSGI configuration file** → Replace content with:
   ```python
   import sys, os
   path = '/home/YOURUSERNAME/AI-Movie-Recommender'
   if path not in sys.path: sys.path.append(path)
   os.environ['FLASK_ENV'] = 'production'
   os.environ['TMDB_API_KEY'] = '89cf1a0e526c7c36bafe8d77248d276d'
   from app import app as application
   ```
5. Replace **YOURUSERNAME** with your actual username
6. Click **Reload** → Your backend is live!

### Step 2: Update Frontend
1. Note your backend URL: `https://YOURUSERNAME.pythonanywhere.com`
2. In your local machine:
   ```bash
   cd "d:\AI Recommendation Engine\recommendation-frontend"
   .\deploy-frontend.bat
   ```
3. Enter your backend URL when prompted
4. Wait for deployment to complete

## 🎉 DONE!
- **Frontend:** https://ai-movie-recommendation-engine.web.app
- **Backend:** https://YOURUSERNAME.pythonanywhere.com

## 🔧 Test URLs:
- Backend health: `https://YOURUSERNAME.pythonanywhere.com/movies/random`
- Frontend: `https://ai-movie-recommendation-engine.web.app`

## 📞 Support:
- **PythonAnywhere:** Great community forums
- **Firebase:** Excellent documentation
- **GitHub:** All code is backed up

## 🎯 Alternative Quick Options:
1. **Render.com:** Connect GitHub → Deploy (sleeps after 15 min)
2. **Railway:** Connect GitHub → Deploy (limited free tier)
3. **Heroku:** Not free anymore
4. **PythonAnywhere:** Recommended (always online, free forever)
