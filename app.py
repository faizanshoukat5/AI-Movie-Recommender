from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD, NMF
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import os
import re
import random
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')
import re
import random
from tmdb_client import TMDBClient
from rating_db import RatingDatabase

app = Flask(__name__)
CORS(app)

# Initialize TMDB client and rating database
tmdb_client = TMDBClient()
rating_db = RatingDatabase()

# Global variables to store multiple trained models and data
models = {
    'svd': None,
    'nmf': None,
    'item_knn': None,
    'user_knn': None,
    'content': None
}
train_user_item_matrix = None
data = None
user_item_matrix = None
movie_titles = {}
movie_genres = {}
item_similarity_matrix = None
user_similarity_matrix = None

def load_movie_titles():
    """Load movie titles and genres from u.item file"""
    movie_titles = {}
    movie_genres = {}
    movies_file = 'ml-100k/u.item'
    
    if os.path.exists(movies_file):
        try:
            with open(movies_file, 'r', encoding='iso-8859-1') as f:
                for line in f:
                    fields = line.strip().split('|')
                    if len(fields) >= 24:  # Ensure we have genre columns
                        movie_id = int(fields[0])
                        movie_title = fields[1]
                        movie_titles[movie_id] = movie_title
                        
                        # Extract genres (columns 5-23 are genre indicators)
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
                        # Fallback for basic title extraction
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
    """Load data and train multiple recommendation models"""
    global models, train_user_item_matrix, data, user_item_matrix, movie_titles, movie_genres
    global item_similarity_matrix, user_similarity_matrix
    
    # Load movie titles and genres
    movie_titles, movie_genres = load_movie_titles()
    
    # Check if data file exists
    data_file = 'ml-100k/u.data'
    if not os.path.exists(data_file):
        raise FileNotFoundError("Data file 'ml-100k/u.data' not found.")
    
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
    
    print("Training multiple recommendation models...")
    
    # 1. SVD Model (Matrix Factorization)
    print("Training SVD model...")
    models['svd'] = TruncatedSVD(n_components=50, random_state=42)
    models['svd'].fit(train_user_item_matrix)
    
    # 2. NMF Model (Non-negative Matrix Factorization)
    print("Training NMF model...")
    models['nmf'] = NMF(n_components=50, random_state=42, max_iter=200)
    models['nmf'].fit(train_user_item_matrix)
    
    # 3. Item-based Collaborative Filtering
    print("Training Item-based KNN...")
    item_item_matrix = train_user_item_matrix.T  # Transpose to get item-user matrix
    models['item_knn'] = NearestNeighbors(n_neighbors=20, metric='cosine')
    models['item_knn'].fit(item_item_matrix)
    
    # Precompute item similarity matrix for faster recommendations
    item_similarity_matrix = cosine_similarity(item_item_matrix)
    
    # 4. User-based Collaborative Filtering
    print("Training User-based KNN...")
    models['user_knn'] = NearestNeighbors(n_neighbors=20, metric='cosine')
    models['user_knn'].fit(train_user_item_matrix)
    
    # Precompute user similarity matrix
    user_similarity_matrix = cosine_similarity(train_user_item_matrix)
    
    # 5. Content-based Filtering
    print("Training Content-based model...")
    # Create content features from genres
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
    
    print("All models trained successfully!")
    return True

def get_svd_recommendations(user_id, n_recommendations=10):
    """Get recommendations using SVD model"""
    if models['svd'] is None:
        return {"error": "SVD model not trained"}
    
    if user_id not in train_user_item_matrix.index:
        return {"error": f"User {user_id} not found in dataset"}
    
    try:
        # Transform the user-item matrix using the trained SVD model
        user_factors = models['svd'].transform(train_user_item_matrix)
        item_factors = models['svd'].components_
        
        # Reconstruct the ratings matrix
        predicted_ratings = np.dot(user_factors, item_factors)
        predicted_ratings_df = pd.DataFrame(predicted_ratings, 
                                          index=train_user_item_matrix.index,
                                          columns=train_user_item_matrix.columns)
        
        # Get items that the user hasn't rated
        user_ratings = train_user_item_matrix.loc[user_id]
        unrated_items = user_ratings[user_ratings == 0].index
        
        # Get predicted ratings for unrated items
        user_predictions = predicted_ratings_df.loc[user_id, unrated_items]
        
        # Get top N recommendations
        top_recommendations = user_predictions.nlargest(n_recommendations)
        
        # Format recommendations with movie titles and posters
        recommendations = []
        for item_id, predicted_rating in top_recommendations.items():
            movie_title = movie_titles.get(item_id, f"Movie {item_id}")
            
            # Get poster URL from cached metadata or fetch from TMDB
            poster_url = None
            try:
                # First try to get from cached metadata
                cached_metadata = rating_db.get_movie_metadata(item_id)
                if cached_metadata and cached_metadata.get('poster_path'):
                    poster_url = tmdb_client.get_poster_url(cached_metadata['poster_path'])
                    print(f"SVD: Found cached poster for movie {item_id}: {poster_url}")
                else:
                    # If not cached, search TMDB directly
                    print(f"SVD: Searching TMDB for movie {item_id} ({movie_title})")
                    search_result = tmdb_client.search_movie(movie_title)
                    if search_result and search_result.get('poster_path'):
                        poster_url = tmdb_client.get_poster_url(search_result['poster_path'])
                        print(f"SVD: Found TMDB poster for movie {item_id}: {poster_url}")
            except Exception as e:
                print(f"SVD: Error getting poster for movie {item_id}: {e}")
                pass
                
            recommendations.append({
                'id': int(item_id),  # MovieCard expects 'id', not 'item_id'
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
    """Get recommendations using NMF model"""
    if models['nmf'] is None:
        return {"error": "NMF model not trained"}
    
    if user_id not in train_user_item_matrix.index:
        return {"error": f"User {user_id} not found in dataset"}
    
    try:
        # Transform the user-item matrix using the trained NMF model
        user_factors = models['nmf'].transform(train_user_item_matrix)
        item_factors = models['nmf'].components_
        
        # Reconstruct the ratings matrix
        predicted_ratings = np.dot(user_factors, item_factors)
        predicted_ratings_df = pd.DataFrame(predicted_ratings, 
                                          index=train_user_item_matrix.index,
                                          columns=train_user_item_matrix.columns)
        
        # Get items that the user hasn't rated
        user_ratings = train_user_item_matrix.loc[user_id]
        unrated_items = user_ratings[user_ratings == 0].index
        
        # Get predicted ratings for unrated items
        user_predictions = predicted_ratings_df.loc[user_id, unrated_items]
        
        # Get top N recommendations
        top_recommendations = user_predictions.nlargest(n_recommendations)
        
        # Format recommendations with movie titles and posters
        recommendations = []
        for item_id, predicted_rating in top_recommendations.items():
            movie_title = movie_titles.get(item_id, f"Movie {item_id}")
            
            # Get poster URL from cached metadata
            poster_url = None
            try:
                cached_metadata = rating_db.get_movie_metadata(item_id)
                if cached_metadata and cached_metadata.get('poster_path'):
                    poster_url = tmdb_client.get_poster_url(cached_metadata['poster_path'])
            except:
                pass
                
            recommendations.append({
                'id': int(item_id),  # MovieCard expects 'id', not 'item_id'
                'item_id': int(item_id),
                'title': movie_title,
                'predicted_rating': round(float(predicted_rating), 2),
                'model': 'NMF',
                'poster_url': poster_url
            })
        
        return recommendations
    
    except Exception as e:
        return {"error": f"Error generating NMF recommendations: {str(e)}"}

def get_item_knn_recommendations(user_id, n_recommendations=10):
    """Get recommendations using item-based KNN (optimized)"""
    if models['item_knn'] is None or item_similarity_matrix is None:
        return {"error": "Item-based KNN model not trained"}
    
    if user_id not in train_user_item_matrix.index:
        return {"error": f"User {user_id} not found in dataset"}
    
    try:
        print(f"Getting item-KNN recommendations for user {user_id}")
        user_ratings = train_user_item_matrix.loc[user_id]
        unrated_items = user_ratings[user_ratings == 0].index
        
        # Limit to top 100 unrated items for speed
        unrated_items = unrated_items[:100]
        
        # Calculate predictions for unrated items (simplified)
        predictions = {}
        rated_items = user_ratings[user_ratings > 0]
        
        for item_id in unrated_items:
            try:
                item_idx = list(train_user_item_matrix.columns).index(item_id)
                
                # Get top 10 similar items for speed
                similarities = []
                for rated_item_id in rated_items.index[:20]:  # Limit to top 20 rated items
                    rated_item_idx = list(train_user_item_matrix.columns).index(rated_item_id)
                    similarity = item_similarity_matrix[item_idx][rated_item_idx]
                    if similarity > 0.1:  # Only consider items with reasonable similarity
                        similarities.append((similarity, rated_items[rated_item_id]))
                
                # Calculate weighted average prediction
                if similarities:
                    similarities.sort(reverse=True)
                    top_similarities = similarities[:10]  # Top 10 similar items
                    numerator = sum(sim * rating for sim, rating in top_similarities)
                    denominator = sum(sim for sim, _ in top_similarities)
                    predictions[item_id] = numerator / denominator if denominator > 0 else 0
            except (ValueError, IndexError):
                continue
        
        # Get top N recommendations
        top_items = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]
        
        # Format recommendations with movie titles and posters
        recommendations = []
        for item_id, predicted_rating in top_items:
            movie_title = movie_titles.get(item_id, f"Movie {item_id}")
            
            # Get poster URL from cached metadata
            poster_url = None
            try:
                cached_metadata = rating_db.get_movie_metadata(item_id)
                if cached_metadata and cached_metadata.get('poster_path'):
                    poster_url = tmdb_client.get_poster_url(cached_metadata['poster_path'])
            except:
                pass
                
            recommendations.append({
                'id': int(item_id),  # MovieCard expects 'id', not 'item_id'
                'item_id': int(item_id),
                'title': movie_title,
                'predicted_rating': round(float(predicted_rating), 2),
                'model': 'Item-KNN',
                'poster_url': poster_url
            })
        
        print(f"Returning {len(recommendations)} item-KNN recommendations")
        return recommendations
    
    except Exception as e:
        print(f"Error in item-KNN: {str(e)}")
        return {"error": f"Error generating Item-KNN recommendations: {str(e)}"}

def get_user_knn_recommendations(user_id, n_recommendations=10):
    """Get recommendations using user-based KNN (optimized)"""
    if models['user_knn'] is None or user_similarity_matrix is None:
        return {"error": "User-based KNN model not trained"}
    
    if user_id not in train_user_item_matrix.index:
        return {"error": f"User {user_id} not found in dataset"}
    
    try:
        print(f"Getting user-KNN recommendations for user {user_id}")
        user_idx = list(train_user_item_matrix.index).index(user_id)
        user_ratings = train_user_item_matrix.loc[user_id]
        unrated_items = user_ratings[user_ratings == 0].index
        
        # Limit to top 100 unrated items for speed
        unrated_items = unrated_items[:100]
        
        # Find top 20 similar users for speed
        user_similarities = user_similarity_matrix[user_idx]
        similar_user_indices = np.argsort(user_similarities)[::-1][1:21]  # Top 20 similar users
        similar_users = []
        
        for idx in similar_user_indices:
            other_user_id = list(train_user_item_matrix.index)[idx]
            similarity = user_similarities[idx]
            if similarity > 0.1:  # Only consider users with reasonable similarity
                similar_users.append((other_user_id, similarity))
        
        # Calculate predictions for unrated items
        predictions = {}
        for item_id in unrated_items:
            # Find similar users who have rated this item
            ratings_from_similar = []
            for similar_user_id, similarity in similar_users:
                similar_user_rating = train_user_item_matrix.loc[similar_user_id, item_id]
                if similar_user_rating > 0:
                    ratings_from_similar.append((similarity, similar_user_rating))
            
            # Calculate weighted average prediction
            if ratings_from_similar:
                ratings_from_similar.sort(reverse=True)
                top_ratings = ratings_from_similar[:10]  # Top 10 similar users
                numerator = sum(sim * rating for sim, rating in top_ratings)
                denominator = sum(sim for sim, _ in top_ratings)
                predictions[item_id] = numerator / denominator if denominator > 0 else 0
        
        # Get top N recommendations
        top_items = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]
        
        # Format recommendations with movie titles and posters
        recommendations = []
        for item_id, predicted_rating in top_items:
            movie_title = movie_titles.get(item_id, f"Movie {item_id}")
            
            # Get poster URL from cached metadata
            poster_url = None
            try:
                cached_metadata = rating_db.get_movie_metadata(item_id)
                if cached_metadata and cached_metadata.get('poster_path'):
                    poster_url = tmdb_client.get_poster_url(cached_metadata['poster_path'])
            except:
                pass
                
            recommendations.append({
                'id': int(item_id),  # MovieCard expects 'id', not 'item_id'
                'item_id': int(item_id),
                'title': movie_title,
                'predicted_rating': round(float(predicted_rating), 2),
                'model': 'User-KNN',
                'poster_url': poster_url
            })
        
        print(f"Returning {len(recommendations)} user-KNN recommendations")
        return recommendations
    
    except Exception as e:
        print(f"Error in user-KNN: {str(e)}")
        return {"error": f"Error generating User-KNN recommendations: {str(e)}"}

def get_content_recommendations(user_id, n_recommendations=10):
    """Get recommendations using content-based filtering"""
    if models['content'] is None:
        return {"error": "Content-based model not trained"}
    
    if user_id not in train_user_item_matrix.index:
        return {"error": f"User {user_id} not found in dataset"}
    
    try:
        user_ratings = train_user_item_matrix.loc[user_id]
        rated_items = user_ratings[user_ratings > 0]
        unrated_items = user_ratings[user_ratings == 0].index
        
        # Get user profile based on rated items
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
        
        # Calculate similarity between user profile and unrated items
        predictions = {}
        for item_id in unrated_items:
            if item_id in models['content']['movie_ids']:
                item_idx = models['content']['movie_ids'].index(item_id)
                item_features = models['content']['content_matrix'][item_idx].toarray().flatten()
                similarity = cosine_similarity([user_profile], [item_features])[0][0]
                predictions[item_id] = similarity
        
        # Get top N recommendations
        top_items = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]
        
        # Format recommendations with movie titles and posters
        recommendations = []
        for item_id, similarity_score in top_items:
            movie_title = movie_titles.get(item_id, f"Movie {item_id}")
            
            # Get poster URL from cached metadata
            poster_url = None
            try:
                cached_metadata = rating_db.get_movie_metadata(item_id)
                if cached_metadata and cached_metadata.get('poster_path'):
                    poster_url = tmdb_client.get_poster_url(cached_metadata['poster_path'])
            except:
                pass
                
            recommendations.append({
                'id': int(item_id),  # MovieCard expects 'id', not 'item_id'
                'item_id': int(item_id),
                'title': movie_title,
                'predicted_rating': round(float(similarity_score * 5), 2),  # Scale similarity to rating
                'model': 'Content-Based',
                'poster_url': poster_url
            })
        
        return recommendations
    
    except Exception as e:
        return {"error": f"Error generating Content-Based recommendations: {str(e)}"}

def get_ensemble_recommendations(user_id, n_recommendations=10, weights=None):
    """Get ensemble recommendations by combining multiple models"""
    if weights is None:
        weights = {'svd': 0.4, 'nmf': 0.3, 'content': 0.3}  # Simplified to faster models
    
    print(f"Getting ensemble recommendations for user {user_id}")
    
    # Get recommendations from each model (only use faster models for ensemble)
    all_recommendations = {}
    
    try:
        # SVD (fast)
        print("Getting SVD recommendations...")
        svd_recs = get_svd_recommendations(user_id, n_recommendations * 2)
        if not isinstance(svd_recs, dict) or 'error' not in svd_recs:
            for rec in svd_recs:
                item_id = rec['item_id']
                if item_id not in all_recommendations:
                    all_recommendations[item_id] = {'scores': {}, 'title': rec['title']}
                all_recommendations[item_id]['scores']['svd'] = rec['predicted_rating']
        
        # NMF (fast)
        print("Getting NMF recommendations...")
        nmf_recs = get_nmf_recommendations(user_id, n_recommendations * 2)
        if not isinstance(nmf_recs, dict) or 'error' not in nmf_recs:
            for rec in nmf_recs:
                item_id = rec['item_id']
                if item_id not in all_recommendations:
                    all_recommendations[item_id] = {'scores': {}, 'title': rec['title']}
                all_recommendations[item_id]['scores']['nmf'] = rec['predicted_rating']
        
        # Content-Based (fast)
        print("Getting Content-based recommendations...")
        content_recs = get_content_recommendations(user_id, n_recommendations * 2)
        if not isinstance(content_recs, dict) or 'error' not in content_recs:
            for rec in content_recs:
                item_id = rec['item_id']
                if item_id not in all_recommendations:
                    all_recommendations[item_id] = {'scores': {}, 'title': rec['title']}
                all_recommendations[item_id]['scores']['content'] = rec['predicted_rating']
        
        # Skip KNN models for now as they are too slow
        
        print(f"Got {len(all_recommendations)} unique recommendations")
        
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
        
        # Format recommendations with posters
        recommendations = []
        for item_id, data in top_items:
            # Get poster URL from cached metadata or fetch from TMDB
            poster_url = None
            try:
                # First try to get from cached metadata
                cached_metadata = rating_db.get_movie_metadata(item_id)
                if cached_metadata and cached_metadata.get('poster_path'):
                    poster_url = tmdb_client.get_poster_url(cached_metadata['poster_path'])
                    print(f"Ensemble: Found cached poster for movie {item_id}: {poster_url}")
                else:
                    # If not cached, search TMDB directly
                    print(f"Ensemble: Searching TMDB for movie {item_id} ({data['title']})")
                    search_result = tmdb_client.search_movie(data['title'])
                    if search_result and search_result.get('poster_path'):
                        poster_url = tmdb_client.get_poster_url(search_result['poster_path'])
                        print(f"Ensemble: Found TMDB poster for movie {item_id}: {poster_url}")
            except Exception as e:
                print(f"Ensemble: Error getting poster for movie {item_id}: {e}")
                pass
                
            recommendations.append({
                'id': int(item_id),  # MovieCard expects 'id', not 'item_id'
                'item_id': int(item_id),
                'title': data['title'],
                'predicted_rating': round(float(data['score']), 2),
                'model': 'Ensemble',
                'model_scores': data['model_scores'],
                'poster_url': poster_url
            })
        
        print(f"Returning {len(recommendations)} ensemble recommendations")
        return recommendations
    
    except Exception as e:
        print(f"Error in ensemble recommendations: {str(e)}")
        return {"error": f"Error generating ensemble recommendations: {str(e)}"}

def get_user_recommendations(user_id, n_recommendations=10, model='ensemble'):
    """Get recommendations for a specific user using specified model"""
    if model == 'svd':
        return get_svd_recommendations(user_id, n_recommendations)
    elif model == 'nmf':
        return get_nmf_recommendations(user_id, n_recommendations)
    elif model == 'item_knn':
        return get_item_knn_recommendations(user_id, n_recommendations)
    elif model == 'user_knn':
        return get_user_knn_recommendations(user_id, n_recommendations)
    elif model == 'content':
        return get_content_recommendations(user_id, n_recommendations)
    elif model == 'ensemble':
        return get_ensemble_recommendations(user_id, n_recommendations)
    else:
        return {"error": f"Unknown model: {model}. Available models: svd, nmf, item_knn, user_knn, content, ensemble"}

def predict_rating(user_id, item_id, model='svd'):
    """Predict rating for a specific user-item pair using specified model"""
    if user_id not in train_user_item_matrix.index:
        return {"error": f"User {user_id} not found in dataset"}
    
    if item_id not in train_user_item_matrix.columns:
        return {"error": f"Item {item_id} not found in dataset"}
    
    try:
        movie_title = movie_titles.get(item_id, f"Movie {item_id}")
        
        if model == 'svd' and models['svd'] is not None:
            user_factors = models['svd'].transform(train_user_item_matrix)
            item_factors = models['svd'].components_
            predicted_ratings = np.dot(user_factors, item_factors)
            predicted_ratings_df = pd.DataFrame(predicted_ratings, 
                                              index=train_user_item_matrix.index,
                                              columns=train_user_item_matrix.columns)
            predicted_rating = predicted_ratings_df.loc[user_id, item_id]
        
        elif model == 'nmf' and models['nmf'] is not None:
            user_factors = models['nmf'].transform(train_user_item_matrix)
            item_factors = models['nmf'].components_
            predicted_ratings = np.dot(user_factors, item_factors)
            predicted_ratings_df = pd.DataFrame(predicted_ratings, 
                                              index=train_user_item_matrix.index,
                                              columns=train_user_item_matrix.columns)
            predicted_rating = predicted_ratings_df.loc[user_id, item_id]
        
        elif model == 'content' and models['content'] is not None:
            # Content-based prediction
            user_ratings = train_user_item_matrix.loc[user_id]
            rated_items = user_ratings[user_ratings > 0]
            
            if len(rated_items) == 0:
                predicted_rating = 2.5  # Default rating if no history
            else:
                # Build user profile
                user_profile = np.zeros(models['content']['content_matrix'].shape[1])
                total_weight = 0
                
                for rated_item_id, rating in rated_items.items():
                    if rated_item_id in models['content']['movie_ids']:
                        item_idx = models['content']['movie_ids'].index(rated_item_id)
                        item_features = models['content']['content_matrix'][item_idx].toarray().flatten()
                        user_profile += item_features * rating
                        total_weight += rating
                
                if total_weight > 0:
                    user_profile = user_profile / total_weight
                
                # Get similarity with target item
                if item_id in models['content']['movie_ids']:
                    item_idx = models['content']['movie_ids'].index(item_id)
                    item_features = models['content']['content_matrix'][item_idx].toarray().flatten()
                    similarity = cosine_similarity([user_profile], [item_features])[0][0]
                    predicted_rating = similarity * 5  # Scale to 1-5 rating
                else:
                    predicted_rating = 2.5  # Default if item not in content matrix
        
        elif model == 'ensemble':
            # Get predictions from multiple models and combine
            predictions = []
            
            # SVD prediction
            if models['svd'] is not None:
                svd_pred = predict_rating(user_id, item_id, 'svd')
                if 'predicted_rating' in svd_pred:
                    predictions.append(svd_pred['predicted_rating'])
            
            # NMF prediction
            if models['nmf'] is not None:
                nmf_pred = predict_rating(user_id, item_id, 'nmf')
                if 'predicted_rating' in nmf_pred:
                    predictions.append(nmf_pred['predicted_rating'])
            
            # Content prediction
            if models['content'] is not None:
                content_pred = predict_rating(user_id, item_id, 'content')
                if 'predicted_rating' in content_pred:
                    predictions.append(content_pred['predicted_rating'])
            
            # Average the predictions
            if predictions:
                predicted_rating = sum(predictions) / len(predictions)
            else:
                predicted_rating = 2.5  # Default rating
        
        else:
            return {"error": f"Model {model} not supported for prediction or not trained"}
        
        # Ensure rating is within valid range (1-5)
        predicted_rating = max(1.0, min(5.0, predicted_rating))
        
        return {
            'user_id': user_id,
            'item_id': item_id,
            'title': movie_title,
            'predicted_rating': round(float(predicted_rating), 2),
            'model': model
        }
    
    except Exception as e:
        print(f"Error in predict_rating: {str(e)}")
        return {"error": f"Error predicting rating: {str(e)}"}

@app.route('/')
def home():
    return jsonify({"message": "AI Movie Recommendation Engine API"})

@app.route('/recommendations/<int:user_id>')
def recommendations(user_id):
    """Get recommendations for a user"""
    n_recommendations = request.args.get('n', 10, type=int)
    model = request.args.get('model', 'ensemble')
    
    result = get_user_recommendations(user_id, n_recommendations, model)
    
    if isinstance(result, dict) and 'error' in result:
        return jsonify(result), 404
    
    return jsonify({
        'recommendations': result,
        'model': model,
        'user_id': user_id
    })

@app.route('/predict')
def predict():
    """Predict rating for a user-item pair"""
    user_id = request.args.get('user_id', type=int)
    item_id = request.args.get('item_id', type=int)
    model = request.args.get('model', 'svd')
    
    if user_id is None or item_id is None:
        return jsonify({'error': 'user_id and item_id are required'}), 400
    
    result = predict_rating(user_id, item_id, model)
    
    if isinstance(result, dict) and 'error' in result:
        return jsonify(result), 404
    
    return jsonify(result)

@app.route('/models')
def get_models():
    """Get available models and their status"""
    model_status = {}
    for model_name, model in models.items():
        if model_name == 'content':
            model_status[model_name] = model is not None and 'tfidf' in model
        else:
            model_status[model_name] = model is not None
    
    return jsonify({
        'models': model_status,
        'available_models': ['svd', 'nmf', 'item_knn', 'user_knn', 'content', 'ensemble']
    })

@app.route('/compare/<int:user_id>')
def compare_models(user_id):
    """Compare recommendations from different models for a user"""
    n_recommendations = request.args.get('n', 10, type=int)
    
    comparison = {}
    model_list = ['svd', 'nmf', 'item_knn', 'user_knn', 'content', 'ensemble']
    
    for model in model_list:
        result = get_user_recommendations(user_id, n_recommendations, model)
        if isinstance(result, dict) and 'error' in result:
            comparison[model] = {'error': result['error']}
        else:
            comparison[model] = result
    
    return jsonify({
        'user_id': user_id,
        'comparison': comparison,
        'n_recommendations': n_recommendations
    })

@app.route('/movies')
def get_movies():
    """Get all movies with basic information and posters"""
    limit = request.args.get('limit', type=int)
    include_posters = request.args.get('include_posters', 'false').lower() == 'true'
    
    movies = []
    movie_items = list(movie_titles.items())
    
    if limit:
        movie_items = movie_items[:limit]
    
    for movie_id, title in movie_items:
        movie_info = {
            'id': movie_id,
            'title': title,
            'year': extract_year(title),
            'genres': movie_genres.get(movie_id, [])
        }
        
        # Add poster URL if requested and available
        if include_posters:
            cached_metadata = rating_db.get_movie_metadata(movie_id)
            if cached_metadata and cached_metadata.get('poster_path'):
                movie_info['poster_url'] = tmdb_client.get_poster_url(cached_metadata['poster_path'])
        
        # Add user rating statistics
        avg_rating, rating_count = rating_db.get_average_rating(movie_id)
        if avg_rating > 0:
            movie_info['user_rating'] = round(avg_rating, 2)
            movie_info['user_rating_count'] = rating_count
        
        movies.append(movie_info)
    
    return jsonify({
        'movies': movies,
        'total': len(movies),
        'has_posters': include_posters
    })

@app.route('/status')
def status():
    """Get system status"""
    model_status = {}
    for model_name, model in models.items():
        if model_name == 'content':
            model_status[model_name] = model is not None and 'tfidf' in model
        else:
            model_status[model_name] = model is not None
    
    return jsonify({
        'status': 'running',
        'models_trained': model_status,
        'total_movies': len(movie_titles),
        'total_users': len(user_item_matrix.index) if user_item_matrix is not None else 0,
        'total_ratings': len(data) if data is not None else 0
    })

@app.route('/search')
def search_movies():
    """Search movies by title with enhanced information"""
    query = request.args.get('q', '').lower()
    sort_by = request.args.get('sort', 'title')
    limit = request.args.get('limit', 50, type=int)
    include_posters = request.args.get('include_posters', 'true').lower() == 'true'
    
    if not query:
        return jsonify({'error': 'Query parameter q is required'}), 400
    
    # Filter movies based on search query
    matching_movies = []
    for movie_id, title in movie_titles.items():
        if query in title.lower():
            movie_info = {
                'id': movie_id,
                'title': title,
                'year': extract_year(title),
                'genres': movie_genres.get(movie_id, [])
            }
            
            # Add poster URL if requested and available
            if include_posters:
                cached_metadata = rating_db.get_movie_metadata(movie_id)
                if cached_metadata and cached_metadata.get('poster_path'):
                    movie_info['poster_url'] = tmdb_client.get_poster_url(cached_metadata['poster_path'])
            
            # Add user rating statistics
            avg_rating, rating_count = rating_db.get_average_rating(movie_id)
            if avg_rating > 0:
                movie_info['user_rating'] = round(avg_rating, 2)
                movie_info['user_rating_count'] = rating_count
            
            matching_movies.append(movie_info)
    
    # Sort results
    if sort_by == 'title':
        matching_movies.sort(key=lambda x: x['title'])
    elif sort_by == 'id':
        matching_movies.sort(key=lambda x: x['id'])
    elif sort_by == 'year':
        matching_movies.sort(key=lambda x: x['year'], reverse=True)
    elif sort_by == 'rating' and any('user_rating' in movie for movie in matching_movies):
        matching_movies.sort(key=lambda x: x.get('user_rating', 0), reverse=True)
    
    # Limit results
    matching_movies = matching_movies[:limit]
    
    return jsonify({
        'movies': matching_movies,
        'total': len(matching_movies),
        'query': query,
        'sort': sort_by,
        'has_posters': include_posters
    })

def extract_year(title):
    """Extract year from movie title"""
    match = re.search(r'\((\d{4})\)', title)
    return int(match.group(1)) if match else 0

@app.route('/movies/random')
def get_random_movies():
    """Get random movies for browsing"""
    limit = request.args.get('limit', 20, type=int)
    include_posters = request.args.get('include_posters', 'false').lower() == 'true'
    
    movie_list = []
    for movie_id, title in movie_titles.items():
        movie_info = {
            'id': movie_id,
            'title': title,
            'year': extract_year(title),
            'genres': movie_genres.get(movie_id, [])
        }
        
        # Add poster URL if requested and available
        has_poster = False
        if include_posters:
            cached_metadata = rating_db.get_movie_metadata(movie_id)
            if cached_metadata and cached_metadata.get('poster_path'):
                movie_info['poster_url'] = tmdb_client.get_poster_url(cached_metadata['poster_path'])
                has_poster = True
        
        # Add user rating statistics
        avg_rating, rating_count = rating_db.get_average_rating(movie_id)
        if avg_rating > 0:
            movie_info['user_rating'] = round(avg_rating, 2)
            movie_info['user_rating_count'] = rating_count
        
        # If posters are requested, only include movies with posters
        if include_posters and not has_poster:
            continue
            
        movie_list.append(movie_info)
    
    if len(movie_list) > limit:
        random_movies = random.sample(movie_list, limit)
    else:
        random_movies = movie_list
    
    return jsonify({
        'movies': random_movies,
        'total': len(random_movies),
        'has_posters': include_posters
    })

@app.route('/movies/<int:movie_id>')
def get_movie_details(movie_id):
    """Get details for a specific movie"""
    if movie_id not in movie_titles:
        return jsonify({'error': f'Movie {movie_id} not found'}), 404
    
    movie_title = movie_titles[movie_id]
    
    # Get some statistics if possible
    movie_stats = {}
    if data is not None:
        movie_data = data[data['item_id'] == movie_id]
        if not movie_data.empty:
            movie_stats = {
                'average_rating': round(movie_data['rating'].mean(), 2),
                'total_ratings': len(movie_data),
                'rating_distribution': movie_data['rating'].value_counts().to_dict()
            }
    
    return jsonify({
        'id': movie_id,
        'title': movie_title,
        'year': extract_year(movie_title),
        'stats': movie_stats
    })

# === NEW ENDPOINTS FOR RATINGS AND MOVIE POSTERS ===

@app.route('/movies/<int:movie_id>/enhanced')
def get_enhanced_movie_details(movie_id):
    """Get enhanced movie details with poster, metadata, and ratings"""
    if movie_id not in movie_titles:
        return jsonify({'error': f'Movie {movie_id} not found'}), 404
    
    movie_title = movie_titles[movie_id]
    
    # Get basic movie info
    movie_info = {
        'id': movie_id,
        'title': movie_title,
        'year': extract_year(movie_title),
        'genres': movie_genres.get(movie_id, [])
    }
    
    # Get cached metadata or fetch from TMDB
    cached_metadata = rating_db.get_movie_metadata(movie_id)
    
    if not cached_metadata:
        # Try to fetch from TMDB
        year = extract_year(movie_title)
        tmdb_data = tmdb_client.search_movie(movie_title, year)
        
        if tmdb_data:
            # Get detailed information
            detailed_data = tmdb_client.get_movie_details(tmdb_data['id'])
            if detailed_data:
                # Cache the metadata
                rating_db.cache_movie_metadata(movie_id, detailed_data)
                cached_metadata = rating_db.get_movie_metadata(movie_id)
    
    # Add TMDB data if available
    if cached_metadata:
        movie_info.update({
            'poster_url': tmdb_client.get_poster_url(cached_metadata.get('poster_path')),
            'backdrop_url': tmdb_client.get_backdrop_url(cached_metadata.get('backdrop_path')),
            'overview': cached_metadata.get('overview'),
            'release_date': cached_metadata.get('release_date'),
            'runtime': cached_metadata.get('runtime'),
            'tmdb_rating': cached_metadata.get('vote_average'),
            'tmdb_votes': cached_metadata.get('vote_count'),
            'cast': cached_metadata.get('cast', []),
            'director': cached_metadata.get('director'),
            'trailer_key': cached_metadata.get('trailer_key')
        })
    
    # Get rating statistics
    avg_rating, rating_count = rating_db.get_average_rating(movie_id)
    movie_info.update({
        'user_rating': round(avg_rating, 2) if avg_rating > 0 else None,
        'user_rating_count': rating_count
    })
    
    # Get original dataset statistics
    if data is not None:
        movie_data = data[data['item_id'] == movie_id]
        if not movie_data.empty:
            movie_info['original_stats'] = {
                'average_rating': round(movie_data['rating'].mean(), 2),
                'total_ratings': len(movie_data),
                'rating_distribution': movie_data['rating'].value_counts().to_dict()
            }
    
    return jsonify(movie_info)

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
    
    # Save the rating
    success = rating_db.add_rating(user_id, movie_id, rating)
    
    if success:
        # Get updated statistics
        avg_rating, rating_count = rating_db.get_average_rating(movie_id)
        
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

@app.route('/movies/<int:movie_id>/rating/<int:user_id>')
def get_user_movie_rating(movie_id, user_id):
    """Get a specific user's rating for a movie"""
    if movie_id not in movie_titles:
        return jsonify({'error': f'Movie {movie_id} not found'}), 404
    
    rating = rating_db.get_movie_rating(user_id, movie_id)
    
    return jsonify({
        'movie_id': movie_id,
        'user_id': user_id,
        'rating': rating,
        'has_rated': rating is not None
    })

@app.route('/users/<int:user_id>/watchlist')
def get_user_watchlist(user_id):
    """Get user's watchlist"""
    watchlist_ids = rating_db.get_watchlist(user_id)
    
    # Enhance with movie information
    watchlist_movies = []
    for movie_id in watchlist_ids:
        if movie_id in movie_titles:
            movie_info = {
                'id': movie_id,
                'title': movie_titles[movie_id],
                'year': extract_year(movie_titles[movie_id]),
                'genres': movie_genres.get(movie_id, [])
            }
            
            # Add poster if available
            cached_metadata = rating_db.get_movie_metadata(movie_id)
            if cached_metadata and cached_metadata.get('poster_path'):
                movie_info['poster_url'] = tmdb_client.get_poster_url(cached_metadata['poster_path'])
            
            watchlist_movies.append(movie_info)
    
    return jsonify({
        'user_id': user_id,
        'watchlist': watchlist_movies,
        'total_movies': len(watchlist_movies)
    })

@app.route('/users/<int:user_id>/watchlist/<int:movie_id>', methods=['POST'])
def add_to_watchlist(user_id, movie_id):
    """Add movie to user's watchlist"""
    if movie_id not in movie_titles:
        return jsonify({'error': f'Movie {movie_id} not found'}), 404
    
    success = rating_db.add_to_watchlist(user_id, movie_id)
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Movie added to watchlist',
            'user_id': user_id,
            'movie_id': movie_id
        })
    else:
        return jsonify({'error': 'Failed to add to watchlist'}), 500

@app.route('/users/<int:user_id>/watchlist/<int:movie_id>', methods=['DELETE'])
def remove_from_watchlist(user_id, movie_id):
    """Remove movie from user's watchlist"""
    if movie_id not in movie_titles:
        return jsonify({'error': f'Movie {movie_id} not found'}), 404
    
    success = rating_db.remove_from_watchlist(user_id, movie_id)
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Movie removed from watchlist',
            'user_id': user_id,
            'movie_id': movie_id
        })
    else:
        return jsonify({'error': 'Failed to remove from watchlist'}), 500

@app.route('/movies/batch-enhance', methods=['POST'])
def batch_enhance_movies():
    """Batch enhance movies with TMDB data"""
    data = request.get_json()
    if not data or 'movie_ids' not in data:
        return jsonify({'error': 'movie_ids array is required'}), 400
    
    movie_ids = data['movie_ids']
    enhanced_movies = []
    
    for movie_id in movie_ids:
        if movie_id in movie_titles:
            movie_info = {
                'id': movie_id,
                'title': movie_titles[movie_id],
                'year': extract_year(movie_titles[movie_id]),
                'genres': movie_genres.get(movie_id, [])
            }
            
            # Get cached metadata
            cached_metadata = rating_db.get_movie_metadata(movie_id)
            if cached_metadata and cached_metadata.get('poster_path'):
                movie_info['poster_url'] = tmdb_client.get_poster_url(cached_metadata['poster_path'])
                movie_info['backdrop_url'] = tmdb_client.get_backdrop_url(cached_metadata.get('backdrop_path'))
                movie_info['overview'] = cached_metadata.get('overview')
                movie_info['tmdb_rating'] = cached_metadata.get('vote_average')
            
            # Get user rating statistics
            avg_rating, rating_count = rating_db.get_average_rating(movie_id)
            movie_info.update({
                'user_rating': round(avg_rating, 2) if avg_rating > 0 else None,
                'user_rating_count': rating_count
            })
            
            enhanced_movies.append(movie_info)
    
    return jsonify({
        'movies': enhanced_movies,
        'total': len(enhanced_movies)
    })

# === END OF NEW ENDPOINTS ===

if __name__ == '__main__':
    # Load data on startup
    load_and_train_model()
    
    # Get port from environment variable or default to 5000
    import os
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    # Start the Flask server
    print(f"Starting Flask server on port {port}")
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
