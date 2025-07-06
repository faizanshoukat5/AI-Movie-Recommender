"""
Production-ready Flask backend with Firebase integration
Enhanced for real-time sync and better performance
"""
from flask import Flask, jsonify, request, g
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore, auth
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD, NMF
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import re
import random
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')
from tmdb_client import TMDBClient
from rating_db import RatingDatabase
import json
from datetime import datetime, timedelta
import threading
import time
from functools import wraps

app = Flask(__name__)
CORS(app)

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate('firebase-service-account.json')
        firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK initialized successfully")
    except Exception as e:
        print(f"Warning: Firebase Admin SDK initialization failed: {e}")
        print("Running in local mode without Firebase integration")

# Initialize clients
tmdb_client = TMDBClient()
rating_db = RatingDatabase()
db = firestore.client() if firebase_admin._apps else None

# Performance optimizations
CACHE_TIMEOUT = 300  # 5 minutes
_cache = {}
_cache_timestamps = {}

def cache_response(timeout=CACHE_TIMEOUT):
    """Cache decorator for expensive operations"""
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

# Firebase Auth middleware
def verify_firebase_token(f):
    """Verify Firebase token for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not db:
            # No Firebase, skip verification
            return f(*args, **kwargs)
        
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        token = auth_header.split(' ')[1]
        try:
            decoded_token = auth.verify_id_token(token)
            g.firebase_user = decoded_token
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Invalid token'}), 401
    
    return decorated_function

# Global variables for ML models
models = {
    'svd': None,
    'nmf': None,
    'content': None
}
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
    movies_file = 'ml-100k/u.item'
    
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
                    elif len(fields) >= 2:
                        movie_id = int(fields[0])
                        movie_title = fields[1]
                        movie_titles[movie_id] = movie_title
                        movie_genres[movie_id] = 'unknown'
                        
            print(f"Loaded {len(movie_titles)} movie titles and genres")
        except Exception as e:
            print(f"Error loading movie titles: {e}")
    else:
        print("Movie titles file (u.item) not found")
    
    return movie_titles, movie_genres

def load_and_train_model():
    """Load data and train optimized models for production"""
    global models, train_user_item_matrix, data, user_item_matrix, movie_titles, movie_genres
    
    # Load movie titles and genres
    movie_titles, movie_genres = load_movie_titles()
    
    # Check if data file exists
    data_file = 'ml-100k/u.data'
    if not os.path.exists(data_file):
        print("Warning: Data file 'ml-100k/u.data' not found. Using minimal setup.")
        return False
    
    try:
        # Load data
        column_names = ['user_id', 'item_id', 'rating', 'timestamp']
        data = pd.read_csv(data_file, sep='\t', names=column_names)
        
        print(f"Loaded {len(data)} ratings from {data['user_id'].nunique()} users and {data['item_id'].nunique()} movies")
        
        # Split data
        train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)
        
        # Create user-item matrices
        def create_user_item_matrix(data):
            return data.pivot_table(index='user_id', columns='item_id', values='rating', fill_value=0)
        
        train_user_item_matrix = create_user_item_matrix(train_data)
        user_item_matrix = create_user_item_matrix(data)
        
        print("Training optimized models for production...")
        
        # 1. SVD Model (Fast and effective)
        print("Training SVD model...")
        models['svd'] = TruncatedSVD(n_components=50, random_state=42)
        models['svd'].fit(train_user_item_matrix)
        
        # 2. NMF Model (Good for interpretability)
        print("Training NMF model...")
        models['nmf'] = NMF(n_components=50, random_state=42, max_iter=200)
        models['nmf'].fit(train_user_item_matrix)
        
        # 3. Content-based Filtering
        print("Training Content-based model...")
        content_features = []
        movie_ids = []
        for movie_id in movie_genres:
            if movie_id in train_user_item_matrix.columns:
                content_features.append(movie_genres[movie_id])
                movie_ids.append(movie_id)
        
        if content_features:
            tfidf = TfidfVectorizer(max_features=100, stop_words='english')
            content_matrix = tfidf.fit_transform(content_features)
            models['content'] = {
                'tfidf': tfidf,
                'content_matrix': content_matrix,
                'movie_ids': movie_ids
            }
        
        print("Models trained successfully!")
        return True
        
    except Exception as e:
        print(f"Error training models: {e}")
        return False

@cache_response(timeout=600)  # Cache for 10 minutes
def get_optimized_recommendations(user_id, n_recommendations=10, model='ensemble'):
    """Get optimized recommendations using fast models"""
    if model == 'svd':
        return get_svd_recommendations(user_id, n_recommendations)
    elif model == 'nmf':
        return get_nmf_recommendations(user_id, n_recommendations)
    elif model == 'content':
        return get_content_recommendations(user_id, n_recommendations)
    else:
        return get_ensemble_recommendations(user_id, n_recommendations)

def get_svd_recommendations(user_id, n_recommendations=10):
    """Fast SVD recommendations"""
    if models['svd'] is None:
        return {"error": "SVD model not trained"}
    
    if user_id not in train_user_item_matrix.index:
        return {"error": f"User {user_id} not found in dataset"}
    
    try:
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
            
            # Get poster URL from cache
            poster_url = None
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
        return {"error": f"Error generating SVD recommendations: {str(e)}"}

def get_nmf_recommendations(user_id, n_recommendations=10):
    """Fast NMF recommendations"""
    if models['nmf'] is None:
        return {"error": "NMF model not trained"}
    
    if user_id not in train_user_item_matrix.index:
        return {"error": f"User {user_id} not found in dataset"}
    
    try:
        user_factors = models['nmf'].transform(train_user_item_matrix)
        item_factors = models['nmf'].components_
        
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
            
            poster_url = None
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
                'model': 'NMF',
                'poster_url': poster_url
            })
        
        return recommendations
    
    except Exception as e:
        return {"error": f"Error generating NMF recommendations: {str(e)}"}

def get_content_recommendations(user_id, n_recommendations=10):
    """Content-based recommendations"""
    if models['content'] is None:
        return {"error": "Content-based model not trained"}
    
    if user_id not in train_user_item_matrix.index:
        return {"error": f"User {user_id} not found in dataset"}
    
    try:
        user_ratings = train_user_item_matrix.loc[user_id]
        rated_items = user_ratings[user_ratings > 0]
        unrated_items = user_ratings[user_ratings == 0].index
        
        user_profile = np.zeros(models['content']['content_matrix'].shape[1])
        total_weight = 0
        
        for item_id, rating in rated_items.items():
            if item_id in models['content']['movie_ids']:
                item_idx = models['content']['movie_ids'].index(item_id)
                item_features = models['content']['content_matrix'][item_idx].toarray().flatten()
                user_profile += item_features * rating
                total_weight += rating
        
        if total_weight > 0:
            user_profile = user_profile / total_weight
        
        predictions = {}
        for item_id in unrated_items:
            if item_id in models['content']['movie_ids']:
                item_idx = models['content']['movie_ids'].index(item_id)
                item_features = models['content']['content_matrix'][item_idx].toarray().flatten()
                similarity = cosine_similarity([user_profile], [item_features])[0][0]
                predictions[item_id] = similarity
        
        top_items = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]
        
        recommendations = []
        for item_id, similarity_score in top_items:
            movie_title = movie_titles.get(item_id, f"Movie {item_id}")
            
            poster_url = None
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
                'predicted_rating': round(float(similarity_score * 5), 2),
                'model': 'Content-Based',
                'poster_url': poster_url
            })
        
        return recommendations
    
    except Exception as e:
        return {"error": f"Error generating Content-Based recommendations: {str(e)}"}

def get_ensemble_recommendations(user_id, n_recommendations=10):
    """Ensemble recommendations using fast models"""
    weights = {'svd': 0.5, 'nmf': 0.3, 'content': 0.2}
    
    all_recommendations = {}
    
    try:
        # Get recommendations from fast models
        for model_name in ['svd', 'nmf', 'content']:
            if model_name == 'svd':
                recs = get_svd_recommendations(user_id, n_recommendations * 2)
            elif model_name == 'nmf':
                recs = get_nmf_recommendations(user_id, n_recommendations * 2)
            else:
                recs = get_content_recommendations(user_id, n_recommendations * 2)
            
            if not isinstance(recs, dict) or 'error' not in recs:
                for rec in recs:
                    item_id = rec['item_id']
                    if item_id not in all_recommendations:
                        all_recommendations[item_id] = {'scores': {}, 'title': rec['title']}
                    all_recommendations[item_id]['scores'][model_name] = rec['predicted_rating']
        
        # Calculate weighted ensemble scores
        ensemble_scores = {}
        for item_id, data in all_recommendations.items():
            weighted_score = 0
            total_weight = 0
            for model, score in data['scores'].items():
                if model in weights:
                    weighted_score += score * weights[model]
                    total_weight += weights[model]
            
            if total_weight > 0:
                ensemble_scores[item_id] = {
                    'score': weighted_score / total_weight,
                    'title': data['title'],
                    'model_scores': data['scores']
                }
        
        # Get top N recommendations
        top_items = sorted(ensemble_scores.items(), key=lambda x: x[1]['score'], reverse=True)[:n_recommendations]
        
        recommendations = []
        for item_id, data in top_items:
            poster_url = None
            try:
                cached_metadata = rating_db.get_movie_metadata(item_id)
                if cached_metadata and cached_metadata.get('poster_path'):
                    poster_url = tmdb_client.get_poster_url(cached_metadata['poster_path'])
            except:
                pass
                
            recommendations.append({
                'id': int(item_id),
                'item_id': int(item_id),
                'title': data['title'],
                'predicted_rating': round(float(data['score']), 2),
                'model': 'Ensemble',
                'model_scores': data['model_scores'],
                'poster_url': poster_url
            })
        
        return recommendations
    
    except Exception as e:
        return {"error": f"Error generating ensemble recommendations: {str(e)}"}

# API Routes
@app.route('/')
def home():
    return jsonify({"message": "AI Movie Recommendation Engine API - Production Ready", "version": "2.0"})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "firebase_connected": db is not None,
        "models_loaded": any(model is not None for model in models.values())
    })

@app.route('/recommendations/<int:user_id>')
@cache_response(timeout=300)
def recommendations(user_id):
    """Get recommendations for a user"""
    n_recommendations = request.args.get('n', 10, type=int)
    model = request.args.get('model', 'ensemble')
    
    result = get_optimized_recommendations(user_id, n_recommendations, model)
    
    if isinstance(result, dict) and 'error' in result:
        return jsonify(result), 404
    
    return jsonify({
        'recommendations': result,
        'model': model,
        'user_id': user_id,
        'cached': True
    })

@app.route('/movies/<int:movie_id>/enhanced')
@cache_response(timeout=1800)  # Cache for 30 minutes
def get_enhanced_movie_details(movie_id):
    """Get enhanced movie details with caching"""
    if movie_id not in movie_titles:
        return jsonify({'error': f'Movie {movie_id} not found'}), 404
    
    movie_title = movie_titles[movie_id]
    
    movie_info = {
        'id': movie_id,
        'title': movie_title,
        'year': extract_year(movie_title),
        'genres': movie_genres.get(movie_id, [])
    }
    
    # Get cached metadata
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
    
    # Get rating statistics
    avg_rating, rating_count = rating_db.get_average_rating(movie_id)
    movie_info.update({
        'user_rating': round(avg_rating, 2) if avg_rating > 0 else None,
        'user_rating_count': rating_count
    })
    
    return jsonify(movie_info)

@app.route('/movies/<int:movie_id>/rate', methods=['POST'])
def rate_movie(movie_id):
    """Rate a movie with Firebase sync"""
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
    
    try:
        # Save to local database
        success = rating_db.add_rating(user_id, movie_id, rating)
        
        if success:
            # Sync to Firebase if available
            if db and hasattr(g, 'firebase_user'):
                try:
                    movie_title = movie_titles[movie_id]
                    
                    # Get movie poster
                    poster_url = None
                    cached_metadata = rating_db.get_movie_metadata(movie_id)
                    if cached_metadata and cached_metadata.get('poster_path'):
                        poster_url = tmdb_client.get_poster_url(cached_metadata['poster_path'])
                    
                    # Update Firebase
                    firebase_rating_data = {
                        'rating': rating,
                        'ratedAt': datetime.now().isoformat(),
                        'movieTitle': movie_title,
                        'moviePoster': poster_url
                    }
                    
                    user_ref = db.collection('users').document(g.firebase_user['uid'])
                    user_ref.update({
                        f'preferences.ratings.{movie_id}': firebase_rating_data
                    })
                    
                    print(f"Rating synced to Firebase for user {g.firebase_user['uid']}")
                except Exception as e:
                    print(f"Firebase sync failed: {e}")
            
            # Get updated statistics
            avg_rating, rating_count = rating_db.get_average_rating(movie_id)
            
            # Clear cache for this movie
            cache_key_pattern = f"get_enhanced_movie_details:({movie_id},)"
            keys_to_remove = [key for key in _cache.keys() if cache_key_pattern in key]
            for key in keys_to_remove:
                _cache.pop(key, None)
                _cache_timestamps.pop(key, None)
            
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
        print(f"Error in rate_movie: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/users/<int:user_id>/ratings')
def get_user_ratings(user_id):
    """Get all ratings for a user"""
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
            cached_metadata = rating_db.get_movie_metadata(movie_id)
            if cached_metadata and cached_metadata.get('poster_path'):
                enhanced_rating['poster_url'] = tmdb_client.get_poster_url(cached_metadata['poster_path'])
            
            enhanced_ratings.append(enhanced_rating)
    
    return jsonify({
        'user_id': user_id,
        'ratings': enhanced_ratings,
        'total_ratings': len(enhanced_ratings)
    })

@app.route('/movies/search')
@cache_response(timeout=300)
def search_movies():
    """Search movies with caching"""
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
                'genres': movie_genres.get(movie_id, [])
            }
            
            # Add poster if requested
            if include_posters:
                cached_metadata = rating_db.get_movie_metadata(movie_id)
                if cached_metadata and cached_metadata.get('poster_path'):
                    movie_info['poster_url'] = tmdb_client.get_poster_url(cached_metadata['poster_path'])
            
            # Add ratings
            avg_rating, rating_count = rating_db.get_average_rating(movie_id)
            if avg_rating > 0:
                movie_info['user_rating'] = round(avg_rating, 2)
                movie_info['user_rating_count'] = rating_count
            
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
@cache_response(timeout=60)  # Cache for 1 minute
def get_random_movies():
    """Get random movies for browsing"""
    limit = request.args.get('limit', 20, type=int)
    include_posters = request.args.get('include_posters', 'true').lower() == 'true'
    
    # Get movies with posters if requested
    movie_list = []
    for movie_id, title in movie_titles.items():
        movie_info = {
            'id': movie_id,
            'title': title,
            'year': extract_year(title),
            'genres': movie_genres.get(movie_id, [])
        }
        
        has_poster = False
        if include_posters:
            cached_metadata = rating_db.get_movie_metadata(movie_id)
            if cached_metadata and cached_metadata.get('poster_path'):
                movie_info['poster_url'] = tmdb_client.get_poster_url(cached_metadata['poster_path'])
                has_poster = True
        
        if include_posters and not has_poster:
            continue
        
        # Add ratings
        avg_rating, rating_count = rating_db.get_average_rating(movie_id)
        if avg_rating > 0:
            movie_info['user_rating'] = round(avg_rating, 2)
            movie_info['user_rating_count'] = rating_count
        
        movie_list.append(movie_info)
    
    # Select random movies
    if len(movie_list) > limit:
        random_movies = random.sample(movie_list, limit)
    else:
        random_movies = movie_list
    
    return jsonify({
        'movies': random_movies,
        'total': len(random_movies),
        'has_posters': include_posters
    })

@app.route('/status')
def status():
    """System status with detailed information"""
    model_status = {}
    for model_name, model in models.items():
        if model_name == 'content':
            model_status[model_name] = model is not None and 'tfidf' in model
        else:
            model_status[model_name] = model is not None
    
    return jsonify({
        'status': 'running',
        'version': '2.0',
        'models_trained': model_status,
        'total_movies': len(movie_titles),
        'total_users': len(user_item_matrix.index) if user_item_matrix is not None else 0,
        'total_ratings': len(data) if data is not None else 0,
        'firebase_connected': db is not None,
        'cache_size': len(_cache),
        'uptime': time.time() - start_time
    })

def extract_year(title):
    """Extract year from movie title"""
    match = re.search(r'\((\d{4})\)', title)
    return int(match.group(1)) if match else 0

# Cache cleanup thread
def cleanup_cache():
    """Clean up expired cache entries"""
    while True:
        current_time = time.time()
        expired_keys = []
        
        for key, timestamp in _cache_timestamps.items():
            if current_time - timestamp > CACHE_TIMEOUT:
                expired_keys.append(key)
        
        for key in expired_keys:
            _cache.pop(key, None)
            _cache_timestamps.pop(key, None)
        
        time.sleep(60)  # Clean up every minute

# Start cache cleanup thread
start_time = time.time()
cleanup_thread = threading.Thread(target=cleanup_cache, daemon=True)
cleanup_thread.start()

if __name__ == '__main__':
    # Load models on startup
    print("Loading models...")
    load_and_train_model()
    
    # Get configuration
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"Starting Production Flask server on port {port}")
    print(f"Firebase integration: {'enabled' if db else 'disabled'}")
    print(f"Models loaded: {sum(1 for model in models.values() if model is not None)}")
    
    # Start server
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
