from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from sklearn.model_selection import train_test_split
import os

app = Flask(__name__)
CORS(app)

# Global variables
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
        raise FileNotFoundError("Data file 'ml-100k/u.data' not found.")
    
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
        user_predictions = predicted_ratings_df.loc[user_id, unrated_items]
        
        # Get top N recommendations
        top_recommendations = user_predictions.nlargest(n_recommendations)
        
        # Format recommendations with movie titles
        recommendations = []
        for item_id, predicted_rating in top_recommendations.items():
            movie_title = movie_titles.get(item_id, f"Movie {item_id}")
            recommendations.append({
                'item_id': int(item_id),
                'title': movie_title,
                'predicted_rating': round(float(predicted_rating), 2)
            })
        
        return recommendations
    
    except Exception as e:
        return {"error": f"Error generating recommendations: {str(e)}"}

def predict_rating(user_id, item_id):
    """Predict rating for a specific user-item pair"""
    global algo, train_user_item_matrix, movie_titles
    
    if algo is None:
        return {"error": "Model not trained"}
    
    if user_id not in train_user_item_matrix.index:
        return {"error": f"User {user_id} not found in dataset"}
    
    if item_id not in train_user_item_matrix.columns:
        return {"error": f"Item {item_id} not found in dataset"}
    
    try:
        # Transform the user-item matrix using the trained SVD model
        user_factors = algo.transform(train_user_item_matrix)
        item_factors = algo.components_
        
        # Reconstruct the ratings matrix
        predicted_ratings = np.dot(user_factors, item_factors)
        predicted_ratings_df = pd.DataFrame(predicted_ratings, 
                                          index=train_user_item_matrix.index,
                                          columns=train_user_item_matrix.columns)
        
        # Get the predicted rating
        predicted_rating = predicted_ratings_df.loc[user_id, item_id]
        movie_title = movie_titles.get(item_id, f"Movie {item_id}")
        
        return {
            'user_id': user_id,
            'item_id': item_id,
            'title': movie_title,
            'predicted_rating': round(float(predicted_rating), 2)
        }
    
    except Exception as e:
        return {"error": f"Error predicting rating: {str(e)}"}

@app.route('/')
def home():
    return jsonify({"message": "AI Movie Recommendation Engine API"})

@app.route('/recommendations/<int:user_id>')
def recommendations(user_id):
    """Get recommendations for a user"""
    n_recommendations = request.args.get('n', 10, type=int)
    result = get_user_recommendations(user_id, n_recommendations)
    
    if isinstance(result, dict) and 'error' in result:
        return jsonify(result), 404
    
    return jsonify({'recommendations': result})

@app.route('/predict')
def predict():
    """Predict rating for a user-item pair"""
    user_id = request.args.get('user_id', type=int)
    item_id = request.args.get('item_id', type=int)
    
    if user_id is None or item_id is None:
        return jsonify({'error': 'user_id and item_id are required'}), 400
    
    result = predict_rating(user_id, item_id)
    
    if isinstance(result, dict) and 'error' in result:
        return jsonify(result), 404
    
    return jsonify(result)

@app.route('/movies')
def get_movies():
    """Get all movies"""
    movies = [{'id': movie_id, 'title': title} for movie_id, title in movie_titles.items()]
    return jsonify({'movies': movies})

@app.route('/status')
def status():
    """Get system status"""
    return jsonify({
        'status': 'running',
        'model_trained': algo is not None,
        'total_movies': len(movie_titles),
        'total_users': len(user_item_matrix.index) if user_item_matrix is not None else 0
    })

if __name__ == '__main__':
    print("Starting AI Movie Recommendation Engine...")
    
    try:
        load_and_train_model()
        print("Server is ready!")
    except Exception as e:
        print(f"Error during startup: {e}")
        print("Server will start but some features may not work.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
