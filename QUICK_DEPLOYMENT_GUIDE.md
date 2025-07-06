# 🚀 QUICK DEPLOYMENT GUIDE - Fix Frontend "Error fetching models"

## Current Issue
Frontend shows: **"Error fetching models: Failed to fetch models"**

## Root Cause
PythonAnywhere backend is missing the `/models` endpoint that the frontend calls on startup.

## Quick Fix Steps

### 1. Copy Complete WSGI Content
Copy the entire content of `wsgi_working.py` (this file has all required endpoints)

### 2. Deploy to PythonAnywhere
1. **Login to PythonAnywhere**
2. **Go to Files tab**
3. **Navigate to: `/home/fizu/AI-Movie-Recommender/`**
4. **Edit `wsgi.py`**
5. **DELETE all existing content**
6. **PASTE the complete content from `wsgi_working.py`**
7. **Save the file**

### 3. Reload Web App
1. **Go to Web tab**
2. **Click "Reload fizu.pythonanywhere.com"**

### 4. Test
Open: `https://fizu.pythonanywhere.com/models`

Should return:
```json
{
  "available_models": ["Popular", "SVD", "NMF", "Content-Based"],
  "default_model": "Popular",
  ...
}
```

## What This Fixes
✅ `/models` endpoint (fixes the error)
✅ `/movies` endpoint  
✅ `/movies/random` endpoint
✅ `/search` endpoint
✅ `/predict` endpoint
✅ `/compare/{user_id}` endpoint
✅ `/users/{user_id}/ratings` endpoint

## Result
✅ Frontend loads without errors
✅ Model dropdown populates
✅ All features work (search, recommendations, ratings)
✅ No more "Error fetching models" error

## Next Steps After Deployment
1. **Test the live app**: https://ai-movie-rec-ca0a4.web.app
2. **Verify all features work**
3. **Check browser console for any remaining errors**

The frontend should now work perfectly! 🎉
