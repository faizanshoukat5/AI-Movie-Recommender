#!/usr/bin/env python3
"""
Database cleanup and initialization script for PythonAnywhere
Run this to fix database schema issues
"""
import os
import sqlite3
import sys

def clean_database():
    """Remove and recreate the database"""
    db_path = '/home/fizu/AI-Movie-Recommender/ratings.db'
    
    print("🔧 Cleaning up database...")
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print("✅ Removed existing database")
    
    # Create new database with proper schema
    print("🔧 Creating new database...")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # User ratings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                movie_id INTEGER NOT NULL,
                rating REAL NOT NULL,
                review TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, movie_id)
            )
        """)
        
        # Movie metadata cache table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movie_metadata (
                movie_id INTEGER PRIMARY KEY,
                tmdb_id INTEGER,
                title TEXT,
                poster_path TEXT,
                backdrop_path TEXT,
                overview TEXT,
                release_date TEXT,
                runtime INTEGER,
                vote_average REAL,
                vote_count INTEGER,
                genres TEXT,
                cast TEXT,
                director TEXT,
                trailer_key TEXT,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User watchlist table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                movie_id INTEGER NOT NULL,
                added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, movie_id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_ratings_user_id ON user_ratings(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_ratings_movie_id ON user_ratings(movie_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_watchlist_user_id ON user_watchlist(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_movie_metadata_tmdb_id ON movie_metadata(tmdb_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_movie_metadata_title ON movie_metadata(title)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_movie_metadata_movie_id ON movie_metadata(movie_id)")
        
        conn.commit()
        print("✅ Database created successfully")
    
    print("🎉 Database cleanup completed!")

def test_database():
    """Test the database"""
    db_path = '/home/fizu/AI-Movie-Recommender/ratings.db'
    
    print("🔍 Testing database...")
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Test tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"✅ Tables found: {tables}")
            
            # Test movie_metadata structure
            cursor.execute("PRAGMA table_info(movie_metadata)")
            columns = [column[1] for column in cursor.fetchall()]
            print(f"✅ movie_metadata columns: {columns}")
            
            # Check if tmdb_id column exists
            if 'tmdb_id' in columns:
                print("✅ tmdb_id column exists")
            else:
                print("❌ tmdb_id column missing")
            
            # Test insert
            cursor.execute("INSERT OR REPLACE INTO user_ratings (user_id, movie_id, rating) VALUES (?, ?, ?)", 
                         ('test_user', 1, 5.0))
            cursor.execute("SELECT * FROM user_ratings WHERE user_id = 'test_user'")
            result = cursor.fetchone()
            if result:
                print("✅ Database insert/select working")
            else:
                print("❌ Database insert/select failed")
            
            conn.commit()
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    return True

def main():
    print("🚀 Database Cleanup and Test Script")
    print("=" * 50)
    
    clean_database()
    
    if test_database():
        print("\n✅ SUCCESS: Database is ready!")
        print("Now reload your PythonAnywhere web app.")
    else:
        print("\n❌ FAILED: Database has issues.")
        print("Check the error messages above.")

if __name__ == "__main__":
    main()
