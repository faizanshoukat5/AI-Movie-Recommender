# 🐍 PythonAnywhere Deployment Guide

## Why PythonAnywhere is Great for Your Flask App:
- ✅ **100% FREE** forever
- ✅ **Python-focused** hosting
- ✅ **No sleeping** - always online
- ✅ **Easy Flask setup**
- ✅ **No credit card** required
- ✅ **Great for beginners**

## 🚀 Step-by-Step Deployment:

### 1. Create PythonAnywhere Account
1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Click **"Create a Beginner account"**
3. Sign up (completely free)

### 2. Upload Your Code
**Option A: Git Clone (Recommended)**
1. Open **Bash Console** in PythonAnywhere
2. Run:
   ```bash
   git clone https://github.com/faizanshoukat5/AI-Movie-Recommender.git
   cd AI-Movie-Recommender
   ```

**Option B: Upload Files**
1. Go to **Files** tab
2. Upload your project files manually

### 3. Install Dependencies
In the **Bash Console**:
```bash
cd AI-Movie-Recommender
pip3.10 install --user -r requirements.txt
```

### 4. Create Web App
1. Go to **Web** tab
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"**
4. Select **Python 3.10**

### 5. Configure WSGI File
1. Click on **WSGI configuration file** link
2. Replace content with:
```python
import sys
import os

# Add your project directory to Python path
path = '/home/yourusername/AI-Movie-Recommender'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['TMDB_API_KEY'] = '89cf1a0e526c7c36bafe8d77248d276d'

from app import app as application

if __name__ == "__main__":
    application.run()
```

### 6. Set Static Files (Optional)
1. In **Web** tab, **Static files** section:
2. Add:
   - URL: `/static/`
   - Directory: `/home/yourusername/AI-Movie-Recommender/static/`

### 7. Reload Web App
1. Click **"Reload yourusername.pythonanywhere.com"**
2. Your backend will be live at: `https://yourusername.pythonanywhere.com`

## 🔧 Your App Structure:
```
/home/yourusername/AI-Movie-Recommender/
├── app.py                 # Main Flask app
├── requirements.txt       # Dependencies
├── ml-100k/              # Dataset
├── tmdb_client.py        # TMDB integration
├── rating_db.py          # Database
└── ...
```

## 📋 PythonAnywhere Free Tier Limits:
- ✅ **Web app:** 1 app always online
- ✅ **Storage:** 512MB
- ✅ **CPU:** 100 CPU seconds/day
- ✅ **Bandwidth:** Reasonable limits
- ⚠️ **Custom domains:** Paid feature only

## 🌐 After Backend Deployment:

### Update Frontend API URL:
1. Copy your PythonAnywhere URL: `https://yourusername.pythonanywhere.com`
2. Update `recommendation-frontend/src/App.js`:
   ```javascript
   const API_BASE_URL = 'https://yourusername.pythonanywhere.com';
   ```
3. Rebuild and redeploy frontend:
   ```bash
   cd recommendation-frontend
   npm run build
   firebase deploy --only hosting
   ```

## 💡 Pro Tips:
- **Always-on:** Your app never sleeps (unlike Render)
- **Great support:** PythonAnywhere has excellent community
- **Educational:** Perfect for learning deployment
- **Reliable:** Rock-solid uptime

## 🔄 Troubleshooting:
- **Import errors:** Check Python path in WSGI file
- **Dependencies:** Install with `pip3.10 install --user`
- **Logs:** Check error logs in Web tab
- **Reload:** Always reload after changes

Your Flask backend will be live at: `https://yourusername.pythonanywhere.com`
