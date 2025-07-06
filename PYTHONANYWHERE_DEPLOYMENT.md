# 🐍 PythonAnywhere Deployment Guide - Production Ready

## Why PythonAnywhere is Great for Your Flask App:
- ✅ **100% FREE** forever
- ✅ **Python-focused** hosting
- ✅ **No sleeping** - always online
- ✅ **Easy Flask setup**
- ✅ **No credit card** required
- ✅ **Production-ready backend**

## 🚀 Complete PythonAnywhere Deployment Instructions

### Step 1: Upload Files to PythonAnywhere

1. **Login to PythonAnywhere** and go to your dashboard
2. **Open a Bash console** and navigate to your project directory:
   ```bash
   cd /home/yourusername/mysite
   ```
3. **Upload the following NEW files** to your PythonAnywhere account:
   - `app_pythonanywhere.py` (production-optimized main application)
   - `config_pythonanywhere.py` (PythonAnywhere-specific configuration)
   - `production_rating_db.py` (enhanced database module)
   - `wsgi.py` (updated WSGI configuration)
   - `requirements_production.txt` (production dependencies)

### Step 2: Install Dependencies

1. **Open a Bash console** in PythonAnywhere
2. **Install required packages**:
   ```bash
   pip3.10 install --user flask flask-cors pandas numpy scikit-learn requests firebase-admin
   ```

### Step 3: Configure Web App

1. **Go to Web tab** in PythonAnywhere dashboard
2. **Edit your existing web app** configuration
3. **Update the WSGI file path** to point to the new `wsgi.py`
4. **Reload your web app**

### Step 4: Update Configuration Files

1. **Edit `wsgi.py`** - Update the path:
   ```python
   path = '/home/yourusername/mysite'  # Replace 'yourusername' with your actual username
   ```

2. **Edit `config_pythonanywhere.py`** - Update paths:
   ```python
   DATABASE_PATH = '/home/yourusername/mysite/ratings.db'
   FIREBASE_SERVICE_ACCOUNT_PATH = '/home/yourusername/mysite/firebase-service-account.json'
   LOG_FILE = '/home/yourusername/mysite/logs/app.log'
   ```

### Step 5: Set Environment Variables

1. **Add to your `wsgi.py` file**:
   ```python
   os.environ['TMDB_API_KEY'] = 'your_tmdb_api_key'
   os.environ['SECRET_KEY'] = 'your_secret_key'
   os.environ['FLASK_ENV'] = 'production'
   ```

### Step 6: Test the New Backend

1. **Reload your web app** in PythonAnywhere
2. **Test the new endpoints**:
   - `https://yourusername.pythonanywhere.com/` (API info with feature status)
   - `https://yourusername.pythonanywhere.com/health` (health check)
   - `https://yourusername.pythonanywhere.com/status` (detailed status)

## 🔧 What's New in the Production Backend

### Enhanced Features
- **Intelligent caching** for better performance
- **Optimized ML models** for PythonAnywhere constraints
- **Enhanced database** with better error handling
- **Production-ready configuration**
- **Comprehensive logging**
- **Health monitoring endpoints**

### Performance Optimizations
- **Reduced ML model components** (25 instead of 50)
- **Lightweight caching system**
- **Optimized database queries**
- **Graceful fallbacks** for missing dependencies

### Improved Error Handling
- **Automatic fallback** to dummy data if dataset missing
- **Graceful degradation** if ML libraries unavailable
- **Comprehensive logging**
- **Better error messages**

## 📊 Monitoring Your Production Backend

### Key Endpoints to Monitor
- `/health` - Basic health check
- `/status` - Detailed system status including:
  - Models loaded
  - Features available
  - Cache status
  - Database connection

### What to Check
1. **Models trained**: Should show which ML models are working
2. **Features available**: Shows what services are operational
3. **Cache size**: Indicates caching is working
4. **Database available**: Confirms database is connected

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. ML Models Not Loading
```bash
# Check if scikit-learn is available
python3.10 -c "import sklearn; print('sklearn available')"
```
**Solution**: The backend will use fallback recommendations if ML models fail

#### 2. Database Issues
```bash
# Check database file permissions
ls -la /home/yourusername/mysite/ratings.db
```
**Solution**: The backend will still work with limited functionality

#### 3. TMDB API Issues
**Solution**: The backend will work without movie posters if TMDB fails

### Debug Mode
1. **Temporarily enable debug**:
   ```python
   os.environ['FLASK_ENV'] = 'development'
   ```
2. **Check error logs** in PythonAnywhere dashboard
3. **Use the `/status` endpoint** to see what's working

## 📱 Update Your Frontend

### Update API URL
Make sure your frontend is pointing to the correct API:
```javascript
REACT_APP_API_URL=https://yourusername.pythonanywhere.com
```

### Test Integration
1. **Deploy your frontend** to Firebase Hosting
2. **Test all features** with the new backend
3. **Check browser console** for any errors
4. **Verify ratings and recommendations** are working

## 🎯 Production Checklist

- [ ] `app_pythonanywhere.py` uploaded and configured
- [ ] `config_pythonanywhere.py` paths updated
- [ ] `wsgi.py` updated with correct paths
- [ ] Dependencies installed via pip
- [ ] Web app reloaded in PythonAnywhere
- [ ] `/health` endpoint returns healthy status
- [ ] `/status` endpoint shows system information
- [ ] Frontend updated with new API URL
- [ ] All features tested end-to-end

## 🚀 Going Live

Your production-ready backend is now available at:
**`https://yourusername.pythonanywhere.com`**

The backend now includes:
- ✅ **Intelligent caching** for better performance
- ✅ **Enhanced error handling** and fallbacks
- ✅ **Production-optimized** ML models
- ✅ **Comprehensive monitoring** endpoints
- ✅ **Better database handling**
- ✅ **Improved logging** and debugging

**Your AI Movie Recommendation Engine is now production-ready!**

## 🚀 **PREFERRED METHOD: GitHub Deployment**

### Why Use GitHub?
- ✅ **Much easier** - Clone with one command
- ✅ **Version control** - Track all changes
- ✅ **Easy updates** - Just `git pull` to update
- ✅ **Professional workflow** - Industry standard
- ✅ **Backup** - Your code is safely stored

### Step 1: Push to GitHub

1. **Initialize Git repository** (if not already done):
   ```bash
   cd "d:\AI Recommendation Engine"
   git init
   git add .
   git commit -m "Production-ready backend with PythonAnywhere optimization"
   ```

2. **Create GitHub repository**:
   - Go to [GitHub.com](https://github.com)
   - Click "New repository"
   - Name it: `ai-movie-recommendation-engine`
   - Make it **Public** (easier for deployment)

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/yourusername/ai-movie-recommendation-engine.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Clone on PythonAnywhere

1. **Open Bash console** in PythonAnywhere
2. **Navigate to your directory**:
   ```bash
   cd /home/yourusername
   ```

3. **Clone your repository**:
   ```bash
   git clone https://github.com/yourusername/ai-movie-recommendation-engine.git mysite
   ```

4. **Install dependencies**:
   ```bash
   cd mysite
   pip3.10 install --user flask flask-cors pandas numpy scikit-learn requests firebase-admin
   ```

### Step 3: Configure PythonAnywhere

1. **Go to Web tab** in PythonAnywhere dashboard
2. **Set Source code** to: `/home/yourusername/mysite`
3. **Set WSGI file** to: `/home/yourusername/mysite/wsgi.py`
4. **Update wsgi.py** with correct path:
   ```python
   path = '/home/yourusername/mysite'  # Replace yourusername
   ```

### Step 4: Easy Updates

Whenever you make changes:
```bash
# On PythonAnywhere bash console
cd /home/yourusername/mysite
git pull origin main
# Reload web app in dashboard
```

That's it! Much easier than manual uploads.

---

## 📁 Alternative: Manual Upload Method

If you prefer not to use GitHub, here's the manual method:
````markdown
# 🐍 PythonAnywhere Deployment Guide - Production Ready

## Why PythonAnywhere is Great for Your Flask App:
- ✅ **100% FREE** forever
- ✅ **Python-focused** hosting
- ✅ **No sleeping** - always online
- ✅ **Easy Flask setup**
- ✅ **No credit card** required
- ✅ **Production-ready backend**

## 🚀 Complete PythonAnywhere Deployment Instructions

### Step 1: Upload Files to PythonAnywhere

1. **Login to PythonAnywhere** and go to your dashboard
2. **Open a Bash console** and navigate to your project directory:
   ```bash
   cd /home/yourusername/mysite
   ```
3. **Upload the following NEW files** to your PythonAnywhere account:
   - `app_pythonanywhere.py` (production-optimized main application)
   - `config_pythonanywhere.py` (PythonAnywhere-specific configuration)
   - `production_rating_db.py` (enhanced database module)
   - `wsgi.py` (updated WSGI configuration)
   - `requirements_production.txt` (production dependencies)

### Step 2: Install Dependencies

1. **Open a Bash console** in PythonAnywhere
2. **Install required packages**:
   ```bash
   pip3.10 install --user flask flask-cors pandas numpy scikit-learn requests firebase-admin
   ```

### Step 3: Configure Web App

1. **Go to Web tab** in PythonAnywhere dashboard
2. **Edit your existing web app** configuration
3. **Update the WSGI file path** to point to the new `wsgi.py`
4. **Reload your web app**

### Step 4: Update Configuration Files

1. **Edit `wsgi.py`** - Update the path:
   ```python
   path = '/home/yourusername/mysite'  # Replace 'yourusername' with your actual username
   ```

2. **Edit `config_pythonanywhere.py`** - Update paths:
   ```python
   DATABASE_PATH = '/home/yourusername/mysite/ratings.db'
   FIREBASE_SERVICE_ACCOUNT_PATH = '/home/yourusername/mysite/firebase-service-account.json'
   LOG_FILE = '/home/yourusername/mysite/logs/app.log'
   ```

### Step 5: Set Environment Variables

1. **Add to your `wsgi.py` file**:
   ```python
   os.environ['TMDB_API_KEY'] = 'your_tmdb_api_key'
   os.environ['SECRET_KEY'] = 'your_secret_key'
   os.environ['FLASK_ENV'] = 'production'
   ```

### Step 6: Test the New Backend

1. **Reload your web app** in PythonAnywhere
2. **Test the new endpoints**:
   - `https://yourusername.pythonanywhere.com/` (API info with feature status)
   - `https://yourusername.pythonanywhere.com/health` (health check)
   - `https://yourusername.pythonanywhere.com/status` (detailed status)

## 🔧 What's New in the Production Backend

### Enhanced Features
- **Intelligent caching** for better performance
- **Optimized ML models** for PythonAnywhere constraints
- **Enhanced database** with better error handling
- **Production-ready configuration**
- **Comprehensive logging**
- **Health monitoring endpoints**

### Performance Optimizations
- **Reduced ML model components** (25 instead of 50)
- **Lightweight caching system**
- **Optimized database queries**
- **Graceful fallbacks** for missing dependencies

### Improved Error Handling
- **Automatic fallback** to dummy data if dataset missing
- **Graceful degradation** if ML libraries unavailable
- **Comprehensive logging**
- **Better error messages**

## 📊 Monitoring Your Production Backend

### Key Endpoints to Monitor
- `/health` - Basic health check
- `/status` - Detailed system status including:
  - Models loaded
  - Features available
  - Cache status
  - Database connection

### What to Check
1. **Models trained**: Should show which ML models are working
2. **Features available**: Shows what services are operational
3. **Cache size**: Indicates caching is working
4. **Database available**: Confirms database is connected

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. ML Models Not Loading
```bash
# Check if scikit-learn is available
python3.10 -c "import sklearn; print('sklearn available')"
```
**Solution**: The backend will use fallback recommendations if ML models fail

#### 2. Database Issues
```bash
# Check database file permissions
ls -la /home/yourusername/mysite/ratings.db
```
**Solution**: The backend will still work with limited functionality

#### 3. TMDB API Issues
**Solution**: The backend will work without movie posters if TMDB fails

### Debug Mode
1. **Temporarily enable debug**:
   ```python
   os.environ['FLASK_ENV'] = 'development'
   ```
2. **Check error logs** in PythonAnywhere dashboard
3. **Use the `/status` endpoint** to see what's working

## 📱 Update Your Frontend

### Update API URL
Make sure your frontend is pointing to the correct API:
```javascript
REACT_APP_API_URL=https://yourusername.pythonanywhere.com
```

### Test Integration
1. **Deploy your frontend** to Firebase Hosting
2. **Test all features** with the new backend
3. **Check browser console** for any errors
4. **Verify ratings and recommendations** are working

## 🎯 Production Checklist

- [ ] `app_pythonanywhere.py` uploaded and configured
- [ ] `config_pythonanywhere.py` paths updated
- [ ] `wsgi.py` updated with correct paths
- [ ] Dependencies installed via pip
- [ ] Web app reloaded in PythonAnywhere
- [ ] `/health` endpoint returns healthy status
- [ ] `/status` endpoint shows system information
- [ ] Frontend updated with new API URL
- [ ] All features tested end-to-end

## 🚀 Going Live

Your production-ready backend is now available at:
**`https://yourusername.pythonanywhere.com`**

The backend now includes:
- ✅ **Intelligent caching** for better performance
- ✅ **Enhanced error handling** and fallbacks
- ✅ **Production-optimized** ML models
- ✅ **Comprehensive monitoring** endpoints
- ✅ **Better database handling**
- ✅ **Improved logging** and debugging

**Your AI Movie Recommendation Engine is now production-ready!**

## 🚀 **PREFERRED METHOD: GitHub Deployment**

### Why Use GitHub?
- ✅ **Much easier** - Clone with one command
- ✅ **Version control** - Track all changes
- ✅ **Easy updates** - Just `git pull` to update
- ✅ **Professional workflow** - Industry standard
- ✅ **Backup** - Your code is safely stored

### Step 1: Push to GitHub

1. **Initialize Git repository** (if not already done):
   ```bash
   cd "d:\AI Recommendation Engine"
   git init
   git add .
   git commit -m "Production-ready backend with PythonAnywhere optimization"
   ```

2. **Create GitHub repository**:
   - Go to [GitHub.com](https://github.com)
   - Click "New repository"
   - Name it: `ai-movie-recommendation-engine`
   - Make it **Public** (easier for deployment)

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/yourusername/ai-movie-recommendation-engine.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Clone on PythonAnywhere

1. **Open Bash console** in PythonAnywhere
2. **Navigate to your directory**:
   ```bash
   cd /home/yourusername
   ```

3. **Clone your repository**:
   ```bash
   git clone https://github.com/yourusername/ai-movie-recommendation-engine.git mysite
   ```

4. **Install dependencies**:
   ```bash
   cd mysite
   pip3.10 install --user flask flask-cors pandas numpy scikit-learn requests firebase-admin
   ```

### Step 3: Configure PythonAnywhere

1. **Go to Web tab** in PythonAnywhere dashboard
2. **Set Source code** to: `/home/yourusername/mysite`
3. **Set WSGI file** to: `/home/yourusername/mysite/wsgi.py`
4. **Update wsgi.py** with correct path:
   ```python
   path = '/home/yourusername/mysite'  # Replace yourusername
   ```

### Step 4: Easy Updates

Whenever you make changes:
```bash
# On PythonAnywhere bash console
cd /home/yourusername/mysite
git pull origin main
# Reload web app in dashboard
```

That's it! Much easier than manual uploads.

---

## 📁 Alternative: Manual Upload Method

If you prefer not to use GitHub, here's the manual method:
````
