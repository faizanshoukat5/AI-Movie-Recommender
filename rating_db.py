"""
Database models for user ratings and movie metadata
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json

class RatingDatabase:
    def __init__(self, db_path: str = "ratings.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # User ratings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    movie_id INTEGER NOT NULL,
                    rating REAL NOT NULL,
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
                    user_id INTEGER NOT NULL,
                    movie_id INTEGER NOT NULL,
                    added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, movie_id)
                )
            """)
            
            conn.commit()
    
    def add_rating(self, user_id: int, movie_id: int, rating: float) -> bool:
        """Add or update a user rating"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO user_ratings (user_id, movie_id, rating, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (user_id, movie_id, rating, datetime.now()))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding rating: {e}")
            return False
    
    def get_user_ratings(self, user_id: int) -> List[Dict]:
        """Get all ratings for a user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT movie_id, rating, timestamp 
                    FROM user_ratings 
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                """, (user_id,))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'movie_id': row[0],
                        'rating': row[1],
                        'timestamp': row[2]
                    })
                return results
        except Exception as e:
            print(f"Error getting user ratings: {e}")
            return []
    
    def get_movie_rating(self, user_id: int, movie_id: int) -> Optional[float]:
        """Get a specific user's rating for a movie"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT rating FROM user_ratings 
                    WHERE user_id = ? AND movie_id = ?
                """, (user_id, movie_id))
                
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"Error getting movie rating: {e}")
            return None
    
    def get_average_rating(self, movie_id: int) -> Tuple[float, int]:
        """Get average rating and count for a movie"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT AVG(rating), COUNT(*) 
                    FROM user_ratings 
                    WHERE movie_id = ?
                """, (movie_id,))
                
                result = cursor.fetchone()
                avg_rating = result[0] if result[0] else 0.0
                count = result[1] if result[1] else 0
                return avg_rating, count
        except Exception as e:
            print(f"Error getting average rating: {e}")
            return 0.0, 0
    
    def cache_movie_metadata(self, movie_id: int, metadata: Dict) -> bool:
        """Cache movie metadata from TMDB"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Extract data from metadata
                tmdb_id = metadata.get('id')
                title = metadata.get('title')
                poster_path = metadata.get('poster_path')
                backdrop_path = metadata.get('backdrop_path')
                overview = metadata.get('overview')
                release_date = metadata.get('release_date')
                runtime = metadata.get('runtime')
                vote_average = metadata.get('vote_average')
                vote_count = metadata.get('vote_count')
                
                # Process genres
                genres = json.dumps([g['name'] for g in metadata.get('genres', [])])
                
                # Process cast (top 5)
                credits = metadata.get('credits', {})
                cast_list = credits.get('cast', [])[:5]
                cast = json.dumps([actor['name'] for actor in cast_list])
                
                # Find director
                crew = credits.get('crew', [])
                director = None
                for person in crew:
                    if person.get('job') == 'Director':
                        director = person.get('name')
                        break
                
                # Find trailer
                videos = metadata.get('videos', {}).get('results', [])
                trailer_key = None
                for video in videos:
                    if video.get('type') == 'Trailer' and video.get('site') == 'YouTube':
                        trailer_key = video.get('key')
                        break
                
                cursor.execute("""
                    INSERT OR REPLACE INTO movie_metadata 
                    (movie_id, tmdb_id, title, poster_path, backdrop_path, overview, 
                     release_date, runtime, vote_average, vote_count, genres, cast, 
                     director, trailer_key, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (movie_id, tmdb_id, title, poster_path, backdrop_path, overview,
                      release_date, runtime, vote_average, vote_count, genres, cast,
                      director, trailer_key, datetime.now()))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error caching movie metadata: {e}")
            return False
    
    def get_movie_metadata(self, movie_id: int) -> Optional[Dict]:
        """Get cached movie metadata"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM movie_metadata WHERE movie_id = ?
                """, (movie_id,))
                
                result = cursor.fetchone()
                if not result:
                    return None
                
                # Convert to dictionary
                columns = [desc[0] for desc in cursor.description]
                metadata = dict(zip(columns, result))
                
                # Parse JSON fields
                if metadata.get('genres'):
                    metadata['genres'] = json.loads(metadata['genres'])
                if metadata.get('cast'):
                    metadata['cast'] = json.loads(metadata['cast'])
                
                return metadata
        except Exception as e:
            print(f"Error getting movie metadata: {e}")
            return None
    
    def add_to_watchlist(self, user_id: int, movie_id: int) -> bool:
        """Add movie to user's watchlist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO user_watchlist (user_id, movie_id)
                    VALUES (?, ?)
                """, (user_id, movie_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding to watchlist: {e}")
            return False
    
    def remove_from_watchlist(self, user_id: int, movie_id: int) -> bool:
        """Remove movie from user's watchlist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM user_watchlist 
                    WHERE user_id = ? AND movie_id = ?
                """, (user_id, movie_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error removing from watchlist: {e}")
            return False
    
    def get_watchlist(self, user_id: int) -> List[int]:
        """Get user's watchlist movie IDs"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT movie_id FROM user_watchlist 
                    WHERE user_id = ? 
                    ORDER BY added_date DESC
                """, (user_id,))
                
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting watchlist: {e}")
            return []

# Initialize database
rating_db = RatingDatabase()
