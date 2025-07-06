"""
Enhanced database module with production-ready features
Supports both SQLite (development) and PostgreSQL (production)
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json
import logging

# Optional PostgreSQL support
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRESQL = True
except ImportError:
    HAS_POSTGRESQL = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionRatingDatabase:
    def __init__(self, db_path: str = "ratings.db", use_postgresql: bool = False):
        self.db_path = db_path
        self.use_postgresql = use_postgresql and HAS_POSTGRESQL
        self.pg_config = None
        
        if self.use_postgresql:
            # Get PostgreSQL configuration from environment
            self.pg_config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': os.getenv('DB_PORT', '5432'),
                'database': os.getenv('DB_NAME', 'movie_recommendations'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', '')
            }
            
            # Test PostgreSQL connection
            try:
                conn = psycopg2.connect(**self.pg_config)
                conn.close()
                logger.info("PostgreSQL connection successful")
            except Exception as e:
                logger.warning(f"PostgreSQL connection failed: {e}. Falling back to SQLite.")
                self.use_postgresql = False
        
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        if self.use_postgresql:
            return psycopg2.connect(**self.pg_config)
        else:
            return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables"""
        if self.use_postgresql:
            self._init_postgresql()
        else:
            self._init_sqlite()
    
    def _init_sqlite(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
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
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_ratings_user_id ON user_ratings(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_ratings_movie_id ON user_ratings(movie_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_watchlist_user_id ON user_watchlist(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_movie_metadata_tmdb_id ON movie_metadata(tmdb_id)")
            
            conn.commit()
            logger.info("SQLite database initialized")
    
    def _init_postgresql(self):
        """Initialize PostgreSQL database"""
        with psycopg2.connect(**self.pg_config) as conn:
            cursor = conn.cursor()
            
            # User ratings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_ratings (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    movie_id INTEGER NOT NULL,
                    rating REAL NOT NULL,
                    review TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
                    genres JSONB,
                    cast JSONB,
                    director TEXT,
                    trailer_key TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User watchlist table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_watchlist (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    movie_id INTEGER NOT NULL,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, movie_id)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_ratings_user_id ON user_ratings(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_ratings_movie_id ON user_ratings(movie_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_watchlist_user_id ON user_watchlist(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_movie_metadata_tmdb_id ON movie_metadata(tmdb_id)")
            
            conn.commit()
            logger.info("PostgreSQL database initialized")
    
    def add_rating(self, user_id: str, movie_id: int, rating: float, review: str = '') -> bool:
        """Add or update a user rating"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.use_postgresql:
                    cursor.execute("""
                        INSERT INTO user_ratings (user_id, movie_id, rating, review, timestamp)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (user_id, movie_id) 
                        DO UPDATE SET rating = EXCLUDED.rating, review = EXCLUDED.review, timestamp = EXCLUDED.timestamp
                    """, (user_id, movie_id, rating, review, datetime.now()))
                else:
                    cursor.execute("""
                        INSERT OR REPLACE INTO user_ratings (user_id, movie_id, rating, review, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                    """, (user_id, movie_id, rating, review, datetime.now()))
                
                conn.commit()
                logger.info(f"Rating added: user={user_id}, movie={movie_id}, rating={rating}")
                return True
        except Exception as e:
            logger.error(f"Error adding rating: {e}")
            return False
    
    def get_user_ratings(self, user_id: str) -> List[Dict]:
        """Get all ratings for a user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.use_postgresql:
                    cursor.execute("""
                        SELECT movie_id, rating, review, timestamp 
                        FROM user_ratings 
                        WHERE user_id = %s
                        ORDER BY timestamp DESC
                    """, (user_id,))
                else:
                    cursor.execute("""
                        SELECT movie_id, rating, review, timestamp 
                        FROM user_ratings 
                        WHERE user_id = ?
                        ORDER BY timestamp DESC
                    """, (user_id,))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'movie_id': row[0],
                        'rating': row[1],
                        'review': row[2] if row[2] else '',
                        'timestamp': row[3]
                    })
                return results
        except Exception as e:
            logger.error(f"Error getting user ratings: {e}")
            return []
    
    def get_movie_rating(self, user_id: str, movie_id: int) -> Optional[float]:
        """Get a specific user's rating for a movie"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.use_postgresql:
                    cursor.execute("""
                        SELECT rating FROM user_ratings 
                        WHERE user_id = %s AND movie_id = %s
                    """, (user_id, movie_id))
                else:
                    cursor.execute("""
                        SELECT rating FROM user_ratings 
                        WHERE user_id = ? AND movie_id = ?
                    """, (user_id, movie_id))
                
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting movie rating: {e}")
            return None
    
    def get_average_rating(self, movie_id: int) -> Tuple[float, int]:
        """Get average rating and count for a movie"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.use_postgresql:
                    cursor.execute("""
                        SELECT AVG(rating), COUNT(*) 
                        FROM user_ratings 
                        WHERE movie_id = %s
                    """, (movie_id,))
                else:
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
            logger.error(f"Error getting average rating: {e}")
            return 0.0, 0
    
    def cache_movie_metadata(self, movie_id: int, metadata: Dict) -> bool:
        """Cache movie metadata from TMDB"""
        try:
            with self.get_connection() as conn:
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
                
                # Process genres and cast
                genres = [g['name'] for g in metadata.get('genres', [])]
                credits = metadata.get('credits', {})
                cast_list = credits.get('cast', [])[:5]
                cast = [actor['name'] for actor in cast_list]
                
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
                
                if self.use_postgresql:
                    cursor.execute("""
                        INSERT INTO movie_metadata 
                        (movie_id, tmdb_id, title, poster_path, backdrop_path, overview, 
                         release_date, runtime, vote_average, vote_count, genres, cast, 
                         director, trailer_key, last_updated)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (movie_id) DO UPDATE SET
                        tmdb_id = EXCLUDED.tmdb_id,
                        title = EXCLUDED.title,
                        poster_path = EXCLUDED.poster_path,
                        backdrop_path = EXCLUDED.backdrop_path,
                        overview = EXCLUDED.overview,
                        release_date = EXCLUDED.release_date,
                        runtime = EXCLUDED.runtime,
                        vote_average = EXCLUDED.vote_average,
                        vote_count = EXCLUDED.vote_count,
                        genres = EXCLUDED.genres,
                        cast = EXCLUDED.cast,
                        director = EXCLUDED.director,
                        trailer_key = EXCLUDED.trailer_key,
                        last_updated = EXCLUDED.last_updated
                    """, (movie_id, tmdb_id, title, poster_path, backdrop_path, overview,
                          release_date, runtime, vote_average, vote_count, json.dumps(genres), 
                          json.dumps(cast), director, trailer_key, datetime.now()))
                else:
                    cursor.execute("""
                        INSERT OR REPLACE INTO movie_metadata 
                        (movie_id, tmdb_id, title, poster_path, backdrop_path, overview, 
                         release_date, runtime, vote_average, vote_count, genres, cast, 
                         director, trailer_key, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (movie_id, tmdb_id, title, poster_path, backdrop_path, overview,
                          release_date, runtime, vote_average, vote_count, json.dumps(genres), 
                          json.dumps(cast), director, trailer_key, datetime.now()))
                
                conn.commit()
                logger.info(f"Movie metadata cached: movie_id={movie_id}, title={title}")
                return True
        except Exception as e:
            logger.error(f"Error caching movie metadata: {e}")
            return False
    
    def get_movie_metadata(self, movie_id: int) -> Optional[Dict]:
        """Get cached movie metadata"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.use_postgresql:
                    cursor.execute("""
                        SELECT * FROM movie_metadata WHERE movie_id = %s
                    """, (movie_id,))
                else:
                    cursor.execute("""
                        SELECT * FROM movie_metadata WHERE movie_id = ?
                    """, (movie_id,))
                
                result = cursor.fetchone()
                if not result:
                    return None
                
                # Convert to dictionary
                if self.use_postgresql:
                    columns = [desc[0] for desc in cursor.description]
                    metadata = dict(zip(columns, result))
                else:
                    cursor.execute("PRAGMA table_info(movie_metadata)")
                    columns = [row[1] for row in cursor.fetchall()]
                    metadata = dict(zip(columns, result))
                
                # Parse JSON fields
                if metadata.get('genres'):
                    if isinstance(metadata['genres'], str):
                        metadata['genres'] = json.loads(metadata['genres'])
                if metadata.get('cast'):
                    if isinstance(metadata['cast'], str):
                        metadata['cast'] = json.loads(metadata['cast'])
                
                return metadata
        except Exception as e:
            logger.error(f"Error getting movie metadata: {e}")
            return None
    
    def add_to_watchlist(self, user_id: str, movie_id: int) -> bool:
        """Add movie to user's watchlist"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.use_postgresql:
                    cursor.execute("""
                        INSERT INTO user_watchlist (user_id, movie_id)
                        VALUES (%s, %s)
                        ON CONFLICT (user_id, movie_id) DO NOTHING
                    """, (user_id, movie_id))
                else:
                    cursor.execute("""
                        INSERT OR IGNORE INTO user_watchlist (user_id, movie_id)
                        VALUES (?, ?)
                    """, (user_id, movie_id))
                
                conn.commit()
                logger.info(f"Movie added to watchlist: user={user_id}, movie={movie_id}")
                return True
        except Exception as e:
            logger.error(f"Error adding to watchlist: {e}")
            return False
    
    def remove_from_watchlist(self, user_id: str, movie_id: int) -> bool:
        """Remove movie from user's watchlist"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.use_postgresql:
                    cursor.execute("""
                        DELETE FROM user_watchlist 
                        WHERE user_id = %s AND movie_id = %s
                    """, (user_id, movie_id))
                else:
                    cursor.execute("""
                        DELETE FROM user_watchlist 
                        WHERE user_id = ? AND movie_id = ?
                    """, (user_id, movie_id))
                
                conn.commit()
                logger.info(f"Movie removed from watchlist: user={user_id}, movie={movie_id}")
                return True
        except Exception as e:
            logger.error(f"Error removing from watchlist: {e}")
            return False
    
    def get_watchlist(self, user_id: str) -> List[int]:
        """Get user's watchlist movie IDs"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.use_postgresql:
                    cursor.execute("""
                        SELECT movie_id FROM user_watchlist 
                        WHERE user_id = %s 
                        ORDER BY added_date DESC
                    """, (user_id,))
                else:
                    cursor.execute("""
                        SELECT movie_id FROM user_watchlist 
                        WHERE user_id = ? 
                        ORDER BY added_date DESC
                    """, (user_id,))
                
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting watchlist: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Total ratings
                cursor.execute("SELECT COUNT(*) FROM user_ratings")
                stats['total_ratings'] = cursor.fetchone()[0]
                
                # Total users
                cursor.execute("SELECT COUNT(DISTINCT user_id) FROM user_ratings")
                stats['total_users'] = cursor.fetchone()[0]
                
                # Total movies with ratings
                cursor.execute("SELECT COUNT(DISTINCT movie_id) FROM user_ratings")
                stats['total_rated_movies'] = cursor.fetchone()[0]
                
                # Total cached metadata
                cursor.execute("SELECT COUNT(*) FROM movie_metadata")
                stats['total_cached_metadata'] = cursor.fetchone()[0]
                
                # Total watchlist items
                cursor.execute("SELECT COUNT(*) FROM user_watchlist")
                stats['total_watchlist_items'] = cursor.fetchone()[0]
                
                stats['database_type'] = 'PostgreSQL' if self.use_postgresql else 'SQLite'
                
                return stats
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}

# Create instance
production_rating_db = ProductionRatingDatabase()
