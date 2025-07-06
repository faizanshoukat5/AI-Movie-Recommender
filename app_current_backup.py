from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import NMF, TruncatedSVD
from sklearn.model_selection import train_test_split
from collections import defaultdict
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variables to store the trained model and data
algo = None
train_user_item_matrix = None
data = None
user_item_matrix = None
movie_titles = {}

def load_movie_titles():
    """Load movie titles from u.item file"""
    movie_titles = {}
    movies_file = 'ml-100k/u.item'
    
    if os.path.exists(movies_file):
        try:
            # Read the u.item file with proper encoding
            with open(movies_file, 'r', encoding='iso-8859-1') as f:
                for line in f:
                    fields = line.strip().split('|')
                    if len(fields) >= 2:
                        movie_id = int(fields[0])
                        movie_title = fields[1]
                        movie_titles[movie_id] = movie_title
            print(f"Loaded {len(movie_titles)} movie titles")
        except Exception as e:
            print(f"Error loading movie titles: {e}")
    else:
        print("Movie titles file (u.item) not found")
    
    return movie_titles

def load_and_train_model():
    """Load data and train the recommendation model"""
    global algo, train_user_item_matrix, data, user_item_matrix, movie_titles
    
    # Load movie titles
    movie_titles = load_movie_titles()
    
    # Check if data file exists
    data_file = 'ml-100k/u.data'
    if not os.path.exists(data_file):
        raise FileNotFoundError("Data file 'ml-100k/u.data' not found. Please ensure the MovieLens dataset is available.")
    
    # Load data
    column_names = ['user_id', 'item_id', 'rating', 'timestamp']
    data = pd.read_csv(data_file, sep='\t', names=column_names)
    
    # Split data
    train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)
    
    # Create user-item matrices
    def create_user_item_matrix(data):
        return data.pivot_table(index='user_id', columns='item_id', values='rating', fill_value=0)
    
    train_user_item_matrix = create_user_item_matrix(train_data)
    user_item_matrix = create_user_item_matrix(data)
    
    # Initialize and train SVD model
    algo = TruncatedSVD(n_components=50, random_state=42)
    algo.fit(train_user_item_matrix)
    
    print("Model trained successfully!")
    return True

def get_user_recommendations(user_id, n_recommendations=10):
    """Get recommendations for a specific user"""
    global algo, train_user_item_matrix, user_item_matrix, movie_titles
    
    if algo is None:
        return {"error": "Model not trained"}
    
    if user_id not in user_item_matrix.index:
        return {"error": f"User {user_id} not found in dataset"}
    
    try:
        # Transform the user-item matrix using the trained SVD model
        user_factors = algo.transform(train_user_item_matrix)
        item_factors = algo.components_
        
        # Reconstruct the ratings matrix
        predicted_ratings = np.dot(user_factors, item_factors)
        predicted_ratings_df = pd.DataFrame(predicted_ratings, 
                                          index=train_user_item_matrix.index,
                                          columns=train_user_item_matrix.columns)
        
        # Get items that the user hasn't rated
        user_ratings = train_user_item_matrix.loc[user_id]
        unrated_items = user_ratings[user_ratings == 0].index
        
        # Get predicted ratings for unrated items
        recommendations = []
        for item in unrated_items:
            if item in predicted_ratings_df.columns:
                predicted_rating = predicted_ratings_df.loc[user_id, item]
                recommendations.append({
                    'item_id': int(item),
                    'movie_title': movie_titles.get(int(item), f"Movie {item}"),
                    'predicted_rating': float(predicted_rating)
                })
        
        # Sort by predicted rating and return top N
        recommendations.sort(key=lambda x: x['predicted_rating'], reverse=True)
        return recommendations[:n_recommendations]
        
    except Exception as e:
        return {"error": str(e)}

def get_user_based_recommendations(user_id, n_recommendations=10):
    """Get user-based collaborative filtering recommendations"""
    global user_item_matrix, movie_titles
    
    if user_id not in user_item_matrix.index:
        return {"error": f"User {user_id} not found in dataset"}
    
    try:
        # Calculate user-user similarity matrix
        user_similarity = cosine_similarity(user_item_matrix)
        user_similarity_df = pd.DataFrame(user_similarity, 
                                        index=user_item_matrix.index, 
                                        columns=user_item_matrix.index)
        
        # Find similar users
        similar_users = user_similarity_df[user_id].sort_values(ascending=False)[1:11]
        
        # Get items that similar users liked but target user hasn't rated
        user_ratings = user_item_matrix.loc[user_id]
        unrated_items = user_ratings[user_ratings == 0].index
        
        # Calculate weighted average ratings for unrated items
        recommendations = {}
        for item in unrated_items:
            weighted_sum = 0
            similarity_sum = 0
            
            for similar_user, similarity_score in similar_users.items():
                if user_item_matrix.loc[similar_user, item] > 0:
                    weighted_sum += similarity_score * user_item_matrix.loc[similar_user, item]
                    similarity_sum += similarity_score
            
            if similarity_sum > 0:
                recommendations[item] = weighted_sum / similarity_sum
        
        # Sort and format recommendations
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                'item_id': int(item_id),
                'movie_title': movie_titles.get(int(item_id), f"Movie {item_id}"),
                'predicted_rating': float(rating)
            }
            for item_id, rating in sorted_recommendations[:n_recommendations]
        ]
        
    except Exception as e:
        return {"error": str(e)}

@app.route('/', methods=['GET'])
def index():
    """Serve the HTML interface"""
    return send_from_directory('.', 'index.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "AI Movie Recommendation Engine",
        "version": "1.0.0",
        "model_trained": algo is not None,
        "data_loaded": data is not None,
        "movie_titles_loaded": len(movie_titles) > 0,
        "total_movies": len(movie_titles),
        "endpoints": {
            "GET /health": "Health check",
            "GET /recommendations/<user_id>": "Get movie recommendations",
            "GET /predict/<user_id>/<item_id>": "Predict rating",
            "GET /users": "Get all users",
            "GET /items": "Get all items",
            "GET /movies/random": "Get random movies",
            "GET /movies/search?q=<query>": "Search movies by title"
        }
    })

@app.route('/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """Get recommendations for a specific user"""
    # Get query parameters
    n = request.args.get('n', default=10, type=int)
    algorithm = request.args.get('algorithm', default='svd', type=str).lower()
    
    # Validate parameters
    if n <= 0 or n > 100:
        return jsonify({"error": "Parameter 'n' must be between 1 and 100"}), 400
    
    if algorithm not in ['svd', 'collaborative']:
        return jsonify({"error": "Algorithm must be 'svd' or 'collaborative'"}), 400
    
    # Get recommendations based on algorithm choice
    if algorithm == 'svd':
        recommendations = get_user_recommendations(user_id, n)
    else:  # collaborative
        recommendations = get_user_based_recommendations(user_id, n)
    
    # Check for errors
    if isinstance(recommendations, dict) and "error" in recommendations:
        return jsonify(recommendations), 404
    
    return jsonify({
        "user_id": user_id,
        "algorithm": algorithm,
        "recommendations": recommendations,
        "count": len(recommendations)
    })

@app.route('/predict/<int:user_id>/<int:item_id>', methods=['GET'])
def predict_rating(user_id, item_id):
    """Predict rating for a specific user-item pair"""
    global algo, train_user_item_matrix
    
    if algo is None:
        return jsonify({"error": "Model not trained"}), 500
    
    if user_id not in train_user_item_matrix.index:
        return jsonify({"error": f"User {user_id} not found in training data"}), 404
    
    if item_id not in train_user_item_matrix.columns:
        return jsonify({"error": f"Item {item_id} not found in training data"}), 404
    
    try:
        # Transform and predict
        user_factors = algo.transform(train_user_item_matrix)
        item_factors = algo.components_
        
        predicted_ratings = np.dot(user_factors, item_factors)
        predicted_ratings_df = pd.DataFrame(predicted_ratings, 
                                          index=train_user_item_matrix.index,
                                          columns=train_user_item_matrix.columns)
        
        predicted_rating = predicted_ratings_df.loc[user_id, item_id]
        
        # Check if user actually rated this item in original data
        actual_rating_check = data[(data['user_id'] == user_id) & (data['item_id'] == item_id)]
        actual_rating = None
        if not actual_rating_check.empty:
            actual_rating = int(actual_rating_check['rating'].iloc[0])
        
        return jsonify({
            "user_id": user_id,
            "item_id": item_id,
            "movie_title": movie_titles.get(item_id, f"Movie {item_id}"),
            "predicted_rating": float(predicted_rating),
            "actual_rating": actual_rating,
            "error": abs(predicted_rating - actual_rating) if actual_rating else None
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users', methods=['GET'])
def get_users():
    """Get list of available users"""
    global user_item_matrix
    
    if user_item_matrix is None:
        return jsonify({"error": "Data not loaded"}), 500
    
    users = sorted(user_item_matrix.index.tolist())
    return jsonify({
        "users": users,
        "count": len(users)
    })

@app.route('/items', methods=['GET'])
def get_items():
    """Get list of available items"""
    global user_item_matrix
    
    if user_item_matrix is None:
        return jsonify({"error": "Data not loaded"}), 500
    
    items = sorted(user_item_matrix.columns.tolist())
    return jsonify({
        "items": items,
        "count": len(items)
    })

@app.route('/movies/random', methods=['GET'])
def get_random_movies():
    """Get random movies for exploration"""
    global movie_titles
    
    if not movie_titles:
        return jsonify({"error": "Movie titles not loaded"}), 500
    
    try:
        # Get random sample of movie IDs
        import random
        random_movie_ids = random.sample(list(movie_titles.keys()), min(20, len(movie_titles)))
        
        movies = []
        for movie_id in random_movie_ids:
            movies.append({
                'item_id': movie_id,
                'movie_title': movie_titles[movie_id]
            })
        
        # Sort by title for better display
        movies.sort(key=lambda x: x['movie_title'])
        
        return jsonify({
            "movies": movies,
            "count": len(movies)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/movies/search', methods=['GET'])
def search_movies():
    """Search movies by title"""
    global movie_titles
    
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    
    if not movie_titles:
        return jsonify({"error": "Movie titles not loaded"}), 500
    
    try:
        # Search for movies containing the query
        matching_movies = []
        for movie_id, title in movie_titles.items():
            if query in title.lower():
                matching_movies.append({
                    'item_id': movie_id,
                    'movie_title': title
                })
        
        # Sort by title and limit results
        matching_movies.sort(key=lambda x: x['movie_title'])
        matching_movies = matching_movies[:50]  # Limit to 50 results
        
        return jsonify({
            "movies": matching_movies,
            "count": len(matching_movies),
            "query": query
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Load and train model on startup
    try:
        load_and_train_model()
        print("🎬 AI Movie Recommendation Engine API Server Starting...")
        print("=" * 60)
        print("Available endpoints:")
        print("  GET /health - Health check")
        print("  GET /recommendations/<user_id>?n=10&algorithm=svd - Get recommendations")
        print("  GET /predict/<user_id>/<item_id> - Predict rating")
        print("  GET /users - Get all users")
        print("  GET /items - Get all items")
        print("  GET /movies/random - Get random movies")
        print("  GET /movies/search?q=<query> - Search movies by title")
        print("\nExample: http://localhost:5000/recommendations/1?n=5&algorithm=svd")
        print("🌐 Frontend: http://localhost:3000")
        print("=" * 60)
        
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Error starting server: {e}")
