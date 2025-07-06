"""
PythonAnywhere-optimized Flask backend for AI Movie Recommendation Engine
Designed specifically for PythonAnywhere hosting environment
"""
from flask import Flask, jsonify, request, g
from flask_cors import CORS
import os
import sys
import logging
from datetime import datetime, timedelta
import json
import time
import threading
from functools import wraps

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import configuration
from config_pythonanywhere import PythonAnywhereConfig

# Import ML and database modules
try:
    import pandas as pd
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.decomposition import TruncatedSVD, NMF
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available. ML features will be limited.")

try:
    from tmdb_client import TMDBClient
    TMDB_AVAILABLE = True
except ImportError:
    TMDB_AVAILABLE = False
    print("Warning: TMDB client not available. Movie posters will not work.")

try:
    from production_rating_db import get_production_rating_db
    PRODUCTION_DB_AVAILABLE = True
except ImportError:
    PRODUCTION_DB_AVAILABLE = False
    try:
        from rating_db import RatingDatabase
        RATING_DB_AVAILABLE = True
    except ImportError:
        RATING_DB_AVAILABLE = False
        print("Warning: No database module available.")

# Firebase integration (optional)
try:
    import firebase_admin
    from firebase_admin import credentials, firestore, auth
    if os.path.exists(PythonAnywhereConfig.FIREBASE_SERVICE_ACCOUNT_PATH):
        if not firebase_admin._apps:
            cred = credentials.Certificate(PythonAnywhereConfig.FIREBASE_SERVICE_ACCOUNT_PATH)
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        FIREBASE_AVAILABLE = True
        print("Firebase integration enabled")
    else:
        FIREBASE_AVAILABLE = False
        db = None
        print("Firebase service account not found - running without Firebase")
except ImportError:
    FIREBASE_AVAILABLE = False
    db = None
    print("Firebase Admin SDK not available - running without Firebase")

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(PythonAnywhereConfig)

# Configure CORS
CORS(app, origins=PythonAnywhereConfig.CORS_ORIGINS)

# Configure logging
logging.basicConfig(
    level=getattr(logging, PythonAnywhereConfig.LOG_LEVEL),
    format=PythonAnywhereConfig.LOG_FORMAT,
    handlers=[
        logging.FileHandler(PythonAnywhereConfig.LOG_FILE) if hasattr(PythonAnywhereConfig, 'LOG_FILE') else logging.StreamHandler(),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize clients
tmdb_client = TMDBClient() if TMDB_AVAILABLE else None
if PRODUCTION_DB_AVAILABLE:
    rating_db = get_production_rating_db()
    # Initialize database safely
    if hasattr(rating_db, 'init_database'):
        rating_db.init_database()
elif RATING_DB_AVAILABLE:
    rating_db = RatingDatabase()
else:
    rating_db = None

# Simple in-memory cache for PythonAnywhere
_cache = {}
_cache_timestamps = {}

def simple_cache(timeout=300):
    """Simple in-memory cache decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Create cache key
            cache_key = f"{f.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # Check if cached and still valid
            if cache_key in _cache and cache_key in _cache_timestamps:
                if time.time() - _cache_timestamps[cache_key] < timeout:
                    return _cache[cache_key]
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            _cache[cache_key] = result
            _cache_timestamps[cache_key] = time.time()
            
            return result
        return decorated_function
    return decorator

# Global variables for ML models
models = {'svd': None, 'nmf': None, 'content': None}
train_user_item_matrix = None
data = None
user_item_matrix = None
movie_titles = {}
movie_genres = {}

def load_movie_titles():
    """Load movie titles and genres from u.item file"""
    global movie_titles, movie_genres
    
    movie_titles = {}
    movie_genres = {}
    movies_file = os.path.join(os.path.dirname(__file__), 'ml-100k', 'u.item')
    
    if os.path.exists(movies_file):
        try:
            with open(movies_file, 'r', encoding='iso-8859-1') as f:
                for line in f:
                    fields = line.strip().split('|')
                    if len(fields) >= 24:
                        movie_id = int(fields[0])
                        movie_title = fields[1]
                        movie_titles[movie_id] = movie_title
                        
                        # Extract genres
                        genre_names = [
                            'unknown', 'Action', 'Adventure', 'Animation', 'Children\'s',
                            'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy',
                            'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance',
                            'Sci-Fi', 'Thriller', 'War', 'Western'
                        ]
                        genres = []
                        for i, genre_flag in enumerate(fields[5:24]):
                            if genre_flag == '1' and i < len(genre_names):
                                genres.append(genre_names[i])
                        movie_genres[movie_id] = ' '.join(genres) if genres else 'unknown'
            
            logger.info(f"Loaded {len(movie_titles)} movie titles and genres")
        except Exception as e:
            logger.error(f"Error loading movie titles: {e}")
            # Create dummy data for testing
            for i in range(1, 11):
                movie_titles[i] = f"Movie {i}"
                movie_genres[i] = "Action"
    else:
        logger.warning("Movie titles file not found. Using dummy data.")
        # Create dummy data for testing
        for i in range(1, 11):
            movie_titles[i] = f"Movie {i}"
            movie_genres[i] = "Action"

def load_and_train_models():
    """Load data and train lightweight models for PythonAnywhere"""
    global models, train_user_item_matrix, data, user_item_matrix
    
    if not SKLEARN_AVAILABLE:
        logger.warning("scikit-learn not available. ML features disabled.")
        return False
    
    # Load movie titles first
    load_movie_titles()
    
    # Check if data file exists
    data_file = os.path.join(os.path.dirname(__file__), 'ml-100k', 'u.data')
    if not os.path.exists(data_file):
        logger.warning("MovieLens dataset not found. Using minimal ML setup.")
        return False
    
    try:
        # Load data
        column_names = ['user_id', 'item_id', 'rating', 'timestamp']
        data = pd.read_csv(data_file, sep='\t', names=column_names)
        
        logger.info(f"Loaded {len(data)} ratings from {data['user_id'].nunique()} users and {data['item_id'].nunique()} movies")
        
        # Split data
        train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)
        
        # Create user-item matrices
        def create_user_item_matrix(data):
            return data.pivot_table(index='user_id', columns='item_id', values='rating', fill_value=0)
        
        train_user_item_matrix = create_user_item_matrix(train_data)
        user_item_matrix = create_user_item_matrix(data)
        
        logger.info("Training lightweight models for PythonAnywhere...")
        
        # Train only fast models for PythonAnywhere
        # 1. SVD Model (reduced components for speed)
        logger.info("Training SVD model...")
        models['svd'] = TruncatedSVD(n_components=25, random_state=42)
        models['svd'].fit(train_user_item_matrix)
        
        # 2. NMF Model (reduced components for speed)
        logger.info("Training NMF model...")
        models['nmf'] = NMF(n_components=25, random_state=42, max_iter=100)
        models['nmf'].fit(train_user_item_matrix)
        
        # 3. Content-based (lightweight)
        logger.info("Training Content-based model...")
        content_features = []
        movie_ids = []
        for movie_id in movie_genres:
            if movie_id in train_user_item_matrix.columns:
                content_features.append(movie_genres[movie_id])
                movie_ids.append(movie_id)
        
        if content_features:
            tfidf = TfidfVectorizer(max_features=50, stop_words='english')
            content_matrix = tfidf.fit_transform(content_features)
            models['content'] = {
                'tfidf': tfidf,
                'content_matrix': content_matrix,
                'movie_ids': movie_ids
            }
        
        logger.info("Models trained successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error training models: {e}")
        return False

def get_simple_recommendations(user_id, n_recommendations=10):
    """Get simple recommendations using available models"""
    if not SKLEARN_AVAILABLE or models['svd'] is None:
        # Return popular movies as fallback
        popular_movies = []
        for movie_id, title in list(movie_titles.items())[:n_recommendations]:
            popular_movies.append({
                'id': movie_id,
                'item_id': movie_id,
                'title': title,
                'predicted_rating': 4.0,
                'model': 'Popular',
                'poster_url': None
            })
        return popular_movies
    
    try:
        if user_id not in train_user_item_matrix.index:
            # Return popular movies for unknown users
            popular_movies = []
            for movie_id, title in list(movie_titles.items())[:n_recommendations]:
                popular_movies.append({
                    'id': movie_id,
                    'item_id': movie_id,
                    'title': title,
                    'predicted_rating': 4.0,
                    'model': 'Popular',
                    'poster_url': None
                })
            return popular_movies
        
        # Use SVD for recommendations
        user_factors = models['svd'].transform(train_user_item_matrix)
        item_factors = models['svd'].components_
        
        predicted_ratings = np.dot(user_factors, item_factors)
        predicted_ratings_df = pd.DataFrame(predicted_ratings, 
                                          index=train_user_item_matrix.index,
                                          columns=train_user_item_matrix.columns)
        
        user_ratings = train_user_item_matrix.loc[user_id]
        unrated_items = user_ratings[user_ratings == 0].index
        
        user_predictions = predicted_ratings_df.loc[user_id, unrated_items]
        top_recommendations = user_predictions.nlargest(n_recommendations)
        
        recommendations = []
        for item_id, predicted_rating in top_recommendations.items():
            movie_title = movie_titles.get(item_id, f"Movie {item_id}")
            
            # Get poster URL if available
            poster_url = None
            if tmdb_client and rating_db:
                try:
                    cached_metadata = rating_db.get_movie_metadata(item_id)
                    if cached_metadata and cached_metadata.get('poster_path'):
                        poster_url = tmdb_client.get_poster_url(cached_metadata['poster_path'])
                except:
                    pass
            
            recommendations.append({
                'id': int(item_id),
                'item_id': int(item_id),
                'title': movie_title,
                'predicted_rating': round(float(predicted_rating), 2),
                'model': 'SVD',
                'poster_url': poster_url
            })
        
        return recommendations
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return []

def extract_year(title):
    """Extract year from movie title"""
    import re
    match = re.search(r'\((\d{4})\)', title)
    return int(match.group(1)) if match else 0

# API Routes
@app.route('/')
def home():
    """Home endpoint with API information"""
    return jsonify({
        "message": "AI Movie Recommendation Engine API - PythonAnywhere Edition",
        "version": "2.0-PA",
        "features": {
            "sklearn_available": SKLEARN_AVAILABLE,
            "tmdb_available": TMDB_AVAILABLE,
            "firebase_available": FIREBASE_AVAILABLE,
            "database_available": rating_db is not None
        },
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "recommendations": "/recommendations/{user_id}",
            "movies": "/movies/search?q=query",
            "random_movies": "/movies/random"
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "platform": "PythonAnywhere",
        "services": {
            "sklearn": SKLEARN_AVAILABLE,
            "tmdb": TMDB_AVAILABLE,
            "firebase": FIREBASE_AVAILABLE,
            "database": rating_db is not None
        }
    })

@app.route('/status')
def status():
    """Detailed status endpoint"""
    model_status = {}
    for model_name, model in models.items():
        if model_name == 'content':
            model_status[model_name] = model is not None and 'tfidf' in model
        else:
            model_status[model_name] = model is not None
    
    return jsonify({
        'status': 'running',
        'version': '2.0-PA',
        'platform': 'PythonAnywhere',
        'models_trained': model_status,
        'total_movies': len(movie_titles),
        'total_users': len(user_item_matrix.index) if user_item_matrix is not None else 0,
        'total_ratings': len(data) if data is not None else 0,
        'features': {
            'sklearn_available': SKLEARN_AVAILABLE,
            'tmdb_available': TMDB_AVAILABLE,
            'firebase_available': FIREBASE_AVAILABLE,
            'database_available': rating_db is not None
        },
        'cache_size': len(_cache)
    })

@app.route('/recommendations/<int:user_id>')
@simple_cache(timeout=300)
def recommendations(user_id):
    """Get recommendations for a user"""
    n_recommendations = request.args.get('n', 10, type=int)
    model = request.args.get('model', 'svd')
    
    try:
        result = get_simple_recommendations(user_id, n_recommendations)
        
        if not result:
            return jsonify({'error': 'No recommendations available'}), 404
        
        return jsonify({
            'recommendations': result,
            'model': model,
            'user_id': user_id,
            'cached': True
        })
    except Exception as e:
        logger.error(f"Error in recommendations: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/movies/search')
@simple_cache(timeout=300)
def search_movies():
    """Search movies with enhanced metadata"""
    query = request.args.get('q', '').lower()
    limit = request.args.get('limit', 50, type=int)
    include_posters = request.args.get('include_posters', 'true').lower() == 'true'
    
    if not query:
        return jsonify({'error': 'Query parameter q is required'}), 400
    
    # Filter movies
    matching_movies = []
    for movie_id, title in movie_titles.items():
        if query in title.lower():
            movie_info = {
                'id': movie_id,
                'title': title,
                'year': extract_year(title),
                'genres': movie_genres.get(movie_id, []),
                # Add required fields with defaults
                'overview': f"Classic movie from the MovieLens dataset: {title}",
                'poster_path': None,
                'backdrop_path': None,
                'release_date': None,
                'vote_average': 0.0,
                'vote_count': 0
            }
            
            # Try to get enhanced metadata
            if tmdb_client and rating_db:
                try:
                    # Check if we have cached metadata
                    cached_metadata = rating_db.get_movie_metadata(movie_id)
                    if cached_metadata:
                        movie_info.update({
                            'overview': cached_metadata.get('overview', movie_info['overview']),
                            'poster_path': cached_metadata.get('poster_path'),
                            'backdrop_path': cached_metadata.get('backdrop_path'),
                            'release_date': cached_metadata.get('release_date'),
                            'vote_average': cached_metadata.get('vote_average', 0.0),
                            'vote_count': cached_metadata.get('vote_count', 0)
                        })
                        
                        # Add poster URL if available
                        if include_posters and cached_metadata.get('poster_path'):
                            movie_info['poster_url'] = tmdb_client.get_poster_url(cached_metadata['poster_path'])
                    else:
                        # Try to fetch from TMDB (limited to avoid rate limits)
                        if tmdb_client and len(matching_movies) < 5:  # Only fetch for first few movies
                            search_results = tmdb_client.search_movie(title)
                            if search_results and search_results.get('results'):
                                tmdb_movie = search_results['results'][0]
                                
                                # Update movie info with TMDB data
                                movie_info.update({
                                    'overview': tmdb_movie.get('overview', movie_info['overview']),
                                    'poster_path': tmdb_movie.get('poster_path'),
                                    'backdrop_path': tmdb_movie.get('backdrop_path'),
                                    'release_date': tmdb_movie.get('release_date'),
                                    'vote_average': tmdb_movie.get('vote_average', 0.0),
                                    'vote_count': tmdb_movie.get('vote_count', 0)
                                })
                                
                                # Cache the metadata
                                rating_db.cache_movie_metadata(movie_id, tmdb_movie)
                                
                                # Add poster URL if available
                                if include_posters and tmdb_movie.get('poster_path'):
                                    movie_info['poster_url'] = tmdb_client.get_poster_url(tmdb_movie['poster_path'])
                                    
                except Exception as e:
                    logger.error(f"Error fetching movie metadata for {movie_id}: {e}")
                    # Keep default values
                    pass
            
            # Add ratings if available
            if rating_db:
                try:
                    avg_rating, rating_count = rating_db.get_average_rating(movie_id)
                    if avg_rating > 0:
                        movie_info['user_rating'] = round(avg_rating, 2)
                        movie_info['user_rating_count'] = rating_count
                except Exception as e:
                    logger.error(f"Error fetching ratings for {movie_id}: {e}")
                    pass
            
            matching_movies.append(movie_info)
    
    # Sort and limit
    matching_movies.sort(key=lambda x: x['title'])
    matching_movies = matching_movies[:limit]
    
    return jsonify({
        'movies': matching_movies,
        'total': len(matching_movies),
        'query': query
    })

@app.route('/movies/random')
@simple_cache(timeout=60)
def get_random_movies():
    """Get random movies for browsing"""
    limit = request.args.get('limit', 20, type=int)
    include_posters = request.args.get('include_posters', 'false').lower() == 'true'
    
    import random
    
    # Get random movies
    all_movies = list(movie_titles.items())
    if len(all_movies) > limit:
        selected_movies = random.sample(all_movies, limit)
    else:
        selected_movies = all_movies
    
    random_movies = []
    for movie_id, title in selected_movies:
        movie_info = {
            'id': movie_id,
            'title': title,
            'year': extract_year(title),
            'genres': movie_genres.get(movie_id, [])
        }
        
        # Add poster if requested and available
        if include_posters and tmdb_client and rating_db:
            try:
                cached_metadata = rating_db.get_movie_metadata(movie_id)
                if cached_metadata and cached_metadata.get('poster_path'):
                    movie_info['poster_url'] = tmdb_client.get_poster_url(cached_metadata['poster_path'])
            except:
                pass
        
        # Add ratings if available
        if rating_db:
            try:
                avg_rating, rating_count = rating_db.get_average_rating(movie_id)
                if avg_rating > 0:
                    movie_info['user_rating'] = round(avg_rating, 2)
                    movie_info['user_rating_count'] = rating_count
            except:
                pass
        
        random_movies.append(movie_info)
    
    return jsonify({
        'movies': random_movies,
        'total': len(random_movies),
        'has_posters': include_posters
    })

@app.route('/movies/<int:movie_id>/rate', methods=['POST'])
def rate_movie(movie_id):
    """Rate a movie"""
    if movie_id not in movie_titles:
        return jsonify({'error': f'Movie {movie_id} not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    user_id = data.get('user_id')
    rating = data.get('rating')
    
    if not user_id or rating is None:
        return jsonify({'error': 'user_id and rating are required'}), 400
    
    if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    if not rating_db:
        return jsonify({'error': 'Rating system not available'}), 503
    
    try:
        # Initialize database if needed
        if hasattr(rating_db, 'initialize_db'):
            rating_db.initialize_db()
        
        # Save the rating
        success = rating_db.add_rating(user_id, movie_id, rating)
        
        if success:
            # Get updated statistics
            try:
                avg_rating, rating_count = rating_db.get_average_rating(movie_id)
            except:
                avg_rating, rating_count = rating, 1
            
            # Clear cache
            _cache.clear()
            _cache_timestamps.clear()
            
            return jsonify({
                'success': True,
                'message': 'Rating saved successfully',
                'movie_id': movie_id,
                'user_id': user_id,
                'rating': rating,
                'average_rating': round(avg_rating, 2),
                'total_ratings': rating_count
            })
        else:
            return jsonify({'error': 'Failed to save rating'}), 500
            
    except Exception as e:
        logger.error(f"Error in rate_movie: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/movies/<int:movie_id>/enhanced')
@simple_cache(timeout=1800)
def get_enhanced_movie_details(movie_id):
    """Get enhanced movie details"""
    if movie_id not in movie_titles:
        return jsonify({'error': f'Movie {movie_id} not found'}), 404
    
    movie_title = movie_titles[movie_id]
    
    movie_info = {
        'id': movie_id,
        'title': movie_title,
        'year': extract_year(movie_title),
        'genres': movie_genres.get(movie_id, [])
    }
    
    # Get cached metadata if available
    if tmdb_client and rating_db:
        try:
            cached_metadata = rating_db.get_movie_metadata(movie_id)
            if cached_metadata:
                movie_info.update({
                    'poster_url': tmdb_client.get_poster_url(cached_metadata.get('poster_path')),
                    'backdrop_url': tmdb_client.get_backdrop_url(cached_metadata.get('backdrop_path')),
                    'overview': cached_metadata.get('overview'),
                    'release_date': cached_metadata.get('release_date'),
                    'runtime': cached_metadata.get('runtime'),
                    'tmdb_rating': cached_metadata.get('vote_average'),
                    'tmdb_votes': cached_metadata.get('vote_count')
                })
        except:
            pass
    
    # Get rating statistics
    if rating_db:
        try:
            avg_rating, rating_count = rating_db.get_average_rating(movie_id)
            movie_info.update({
                'user_rating': round(avg_rating, 2) if avg_rating > 0 else None,
                'user_rating_count': rating_count
            })
        except:
            pass
    
    return jsonify(movie_info)

@app.route('/users/<user_id>/ratings')
def get_user_ratings(user_id):
    """Get all ratings for a user"""
    if not rating_db:
        return jsonify({'error': 'Rating system not available'}), 503
    
    try:
        ratings = rating_db.get_user_ratings(user_id)
        
        # Enhance with movie information
        enhanced_ratings = []
        for rating in ratings:
            movie_id = rating['movie_id']
            if movie_id in movie_titles:
                enhanced_rating = {
                    'movie_id': movie_id,
                    'title': movie_titles[movie_id],
                    'year': extract_year(movie_titles[movie_id]),
                    'rating': rating['rating'],
                    'timestamp': rating['timestamp']
                }
                
                # Add poster if available
                if tmdb_client:
                    try:
                        cached_metadata = rating_db.get_movie_metadata(movie_id)
                        if cached_metadata and cached_metadata.get('poster_path'):
                            enhanced_rating['poster_url'] = tmdb_client.get_poster_url(cached_metadata['poster_path'])
                    except:
                        pass
                
                enhanced_ratings.append(enhanced_rating)
        
        return jsonify({
            'user_id': user_id,
            'ratings': enhanced_ratings,
            'total_ratings': len(enhanced_ratings)
        })
    except Exception as e:
        logger.error(f"Error getting user ratings: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Cache cleanup function
def cleanup_cache():
    """Clean up expired cache entries"""
    while True:
        try:
            current_time = time.time()
            expired_keys = []
            
            for key, timestamp in _cache_timestamps.items():
                if current_time - timestamp > 3600:  # 1 hour
                    expired_keys.append(key)
            
            for key in expired_keys:
                _cache.pop(key, None)
                _cache_timestamps.pop(key, None)
            
            time.sleep(300)  # Clean up every 5 minutes
        except Exception as e:
            logger.error(f"Error in cache cleanup: {e}")
            time.sleep(60)

# Initialize the application
def initialize_app():
    """Initialize the application"""
    try:
        logger.info("Initializing AI Movie Recommendation Engine for PythonAnywhere...")
        
        # Load movie data
        load_movie_titles()
        
        # Train models if sklearn is available
        if SKLEARN_AVAILABLE:
            success = load_and_train_models()
            if success:
                logger.info("Models trained successfully")
            else:
                logger.warning("Model training failed, using fallback methods")
        
        # Start cache cleanup thread
        cleanup_thread = threading.Thread(target=cleanup_cache, daemon=True)
        cleanup_thread.start()
        
        logger.info("Application initialized successfully")
        
    except Exception as e:
        logger.error(f"Error during initialization: {e}")

# Initialize when module is imported
initialize_app()

# WSGI application
application = app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
