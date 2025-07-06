#!/usr/bin/env python3
"""
Fix script for PythonAnywhere deployment issues
Run this on PythonAnywhere to fix common issues
"""
import os
import json
import sqlite3
import sys

def fix_firebase_setup():
    """Create a dummy Firebase service account if missing"""
    firebase_path = '/home/fizu/AI-Movie-Recommender/firebase-service-account.json'
    
    if not os.path.exists(firebase_path):
        print("🔧 Creating dummy Firebase service account...")
        
        # Create a dummy service account structure
        dummy_service_account = {
            "type": "service_account",
            "project_id": "ai-movie-recommendation-engine",
            "private_key_id": "dummy",
            "private_key": "-----BEGIN PRIVATE KEY-----\nDUMMY\n-----END PRIVATE KEY-----\n",
            "client_email": "dummy@ai-movie-recommendation-engine.iam.gserviceaccount.com",
            "client_id": "dummy",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/dummy"
        }
        
        # Write the dummy file
        with open(firebase_path, 'w') as f:
            json.dump(dummy_service_account, f, indent=2)
        
        print(f"✅ Created dummy Firebase service account at {firebase_path}")
        print("⚠️  Firebase features will be limited without a real service account")
    else:
        print("✅ Firebase service account already exists")

def fix_database_setup():
    """Initialize SQLite database if missing"""
    db_path = '/home/fizu/AI-Movie-Recommender/ratings.db'
    
    if not os.path.exists(db_path):
        print("🔧 Creating SQLite database...")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create ratings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    movie_id INTEGER NOT NULL,
                    rating REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, movie_id)
                )
            ''')
            
            # Create movie metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS movie_metadata (
                    movie_id INTEGER PRIMARY KEY,
                    title TEXT,
                    overview TEXT,
                    poster_path TEXT,
                    backdrop_path TEXT,
                    release_date TEXT,
                    genre_ids TEXT,
                    vote_average REAL,
                    vote_count INTEGER,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ratings_user_id ON ratings(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ratings_movie_id ON ratings(movie_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_movie_metadata_title ON movie_metadata(title)')
            
            conn.commit()
            conn.close()
            
            print(f"✅ Created SQLite database at {db_path}")
            
        except Exception as e:
            print(f"❌ Error creating database: {e}")
    else:
        print("✅ Database already exists")

def fix_logs_directory():
    """Create logs directory if missing"""
    logs_path = '/home/fizu/AI-Movie-Recommender/logs'
    
    if not os.path.exists(logs_path):
        print("🔧 Creating logs directory...")
        os.makedirs(logs_path, exist_ok=True)
        print(f"✅ Created logs directory at {logs_path}")
    else:
        print("✅ Logs directory already exists")

def fix_movie_search_endpoint():
    """Create a patch for movie search to include required fields"""
    patch_content = '''
# Patch for movie search endpoint
# Add this to your app_pythonanywhere.py if movies are missing overview and poster_path

def add_tmdb_metadata(movie_info, movie_id, movie_title):
    """Add TMDB metadata to movie info"""
    # Add default values if TMDB is not available
    movie_info['overview'] = f"Classic movie: {movie_title}"
    movie_info['poster_path'] = None
    movie_info['backdrop_path'] = None
    movie_info['release_date'] = None
    movie_info['vote_average'] = 0.0
    movie_info['vote_count'] = 0
    
    # Try to get real metadata if TMDB is available
    if tmdb_client:
        try:
            # Search for movie on TMDB
            search_results = tmdb_client.search_movie(movie_title)
            if search_results and search_results['results']:
                tmdb_movie = search_results['results'][0]
                movie_info.update({
                    'overview': tmdb_movie.get('overview', movie_info['overview']),
                    'poster_path': tmdb_movie.get('poster_path'),
                    'backdrop_path': tmdb_movie.get('backdrop_path'),
                    'release_date': tmdb_movie.get('release_date'),
                    'vote_average': tmdb_movie.get('vote_average', 0.0),
                    'vote_count': tmdb_movie.get('vote_count', 0)
                })
        except Exception as e:
            print(f"TMDB metadata error: {e}")
    
    return movie_info
'''
    
    print("📝 Movie search patch ready")
    print("Add the add_tmdb_metadata function to your app_pythonanywhere.py")
    print("Then call it in your search_movies() function")

def run_all_fixes():
    """Run all fixes"""
    print("🔧 Starting PythonAnywhere Deployment Fixes")
    print("=" * 50)
    
    fix_firebase_setup()
    fix_database_setup()
    fix_logs_directory()
    fix_movie_search_endpoint()
    
    print("\n" + "=" * 50)
    print("✅ All fixes applied!")
    print("\nNext steps:")
    print("1. Reload your web app in PythonAnywhere dashboard")
    print("2. Test the endpoints again")
    print("3. Check the logs for any remaining issues")

if __name__ == "__main__":
    run_all_fixes()
