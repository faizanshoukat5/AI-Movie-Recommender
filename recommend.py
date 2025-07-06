# Import libraries
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import NMF, TruncatedSVD
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
from collections import defaultdict
import os

def get_top_n(predictions, n=5):
    """Get top N recommendations for each user from predictions"""
    top_n = defaultdict(list)
    
    # Group predictions by user
    for pred in predictions:
        uid = pred['user_id']
        iid = pred['item_id']
        est = pred['predicted_rating']
        top_n[uid].append((iid, est))
    
    # Sort each user's predictions by estimated rating and take top N
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]
    
    return top_n

# Load movie titles
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

# Load movie titles at startup
movie_titles = load_movie_titles()

# Check if data file exists
data_file = 'ml-100k/u.data'
if os.path.exists(data_file):
    # Load data using pandas
    # MovieLens 100K format: user_id, item_id, rating, timestamp
    column_names = ['user_id', 'item_id', 'rating', 'timestamp']
    data = pd.read_csv(data_file, sep='\t', names=column_names)
    
    print("Dataset loaded successfully.")
    print(f"Dataset shape: {data.shape}")
    print(f"Number of users: {data['user_id'].nunique()}")
    print(f"Number of items: {data['item_id'].nunique()}")
    print(f"Rating range: {data['rating'].min()} to {data['rating'].max()}")
    print("\nFirst few rows:")
    print(data.head())
else:
    print("Data file not found. Please make sure 'ml-100k/u.data' exists in the current directory.")
    print("You can download the MovieLens 100K dataset from:")
    print("https://grouplens.org/datasets/movielens/100k/")

# Split data: 80% training, 20% testing
train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)

print("\nTrain and test sets created.")
print(f"Training set shape: {train_data.shape}")
print(f"Testing set shape: {test_data.shape}")
print(f"Training set size: {len(train_data)} ratings")
print(f"Testing set size: {len(test_data)} ratings")

# Create a user-item matrix
def create_user_item_matrix(data):
    """Create a user-item matrix from the ratings data"""
    return data.pivot_table(index='user_id', columns='item_id', values='rating', fill_value=0)

# Create separate user-item matrices for training and testing
train_user_item_matrix = create_user_item_matrix(train_data)
test_user_item_matrix = create_user_item_matrix(test_data)

print(f"Training user-item matrix shape: {train_user_item_matrix.shape}")
print(f"Testing user-item matrix shape: {test_user_item_matrix.shape}")

# Import SVD model (using scikit-learn's TruncatedSVD)
# Initialize the SVD model
# TruncatedSVD is equivalent to SVD in collaborative filtering
algo = TruncatedSVD(n_components=50, random_state=42)

print("\nSVD model initialized.")
print(f"SVD components: {algo.n_components}")

# Train the model on training data
algo.fit(train_user_item_matrix)

print("Model trained successfully.")

# Simple collaborative filtering using cosine similarity
def get_user_based_recommendations(user_id, user_item_matrix, n_recommendations=10):
    """Get recommendations for a user based on similar users"""
    
    # Calculate user-user similarity matrix
    user_similarity = cosine_similarity(user_item_matrix)
    user_similarity_df = pd.DataFrame(user_similarity, 
                                    index=user_item_matrix.index, 
                                    columns=user_item_matrix.index)
    
    # Find similar users to the target user
    similar_users = user_similarity_df[user_id].sort_values(ascending=False)[1:11]  # Top 10 similar users
    
    # Get items that similar users liked but target user hasn't rated
    user_ratings = user_item_matrix.loc[user_id]
    unrated_items = user_ratings[user_ratings == 0].index
    
    # Calculate weighted average ratings for unrated items
    recommendations = {}
    for item in unrated_items:
        weighted_sum = 0
        similarity_sum = 0
        
        for similar_user, similarity_score in similar_users.items():
            if user_item_matrix.loc[similar_user, item] > 0:  # Similar user has rated this item
                weighted_sum += similarity_score * user_item_matrix.loc[similar_user, item]
                similarity_sum += similarity_score
        
        if similarity_sum > 0:
            recommendations[item] = weighted_sum / similarity_sum
    
    # Sort recommendations by predicted rating
    sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
    
    return sorted_recommendations[:n_recommendations]

# Matrix Factorization using NMF
def get_matrix_factorization_recommendations(user_id, user_item_matrix, n_recommendations=10):
    """Get recommendations using Non-negative Matrix Factorization"""
    
    # Apply NMF
    nmf = NMF(n_components=50, random_state=42, max_iter=100)
    user_features = nmf.fit_transform(user_item_matrix)
    item_features = nmf.components_
    
    # Reconstruct the user-item matrix
    predicted_ratings = np.dot(user_features, item_features)
    predicted_ratings_df = pd.DataFrame(predicted_ratings, 
                                      index=user_item_matrix.index,
                                      columns=user_item_matrix.columns)
    
    # Get items that the user hasn't rated
    user_ratings = user_item_matrix.loc[user_id]
    unrated_items = user_ratings[user_ratings == 0].index
    
    # Get predicted ratings for unrated items
    recommendations = []
    for item in unrated_items:
        predicted_rating = predicted_ratings_df.loc[user_id, item]
        recommendations.append((item, predicted_rating))
    
    # Sort by predicted rating
    recommendations.sort(key=lambda x: x[1], reverse=True)
    
    return recommendations[:n_recommendations]

# Function to get SVD-based recommendations
def get_svd_recommendations(user_id, user_item_matrix, svd_model, n_recommendations=10):
    """Get recommendations using trained SVD model"""
    
    # Transform the user-item matrix
    user_factors = svd_model.transform(user_item_matrix)
    item_factors = svd_model.components_
    
    # Reconstruct the ratings matrix
    predicted_ratings = np.dot(user_factors, item_factors)
    predicted_ratings_df = pd.DataFrame(predicted_ratings, 
                                      index=user_item_matrix.index,
                                      columns=user_item_matrix.columns)
    
    # Get items that the user hasn't rated
    user_ratings = user_item_matrix.loc[user_id]
    unrated_items = user_ratings[user_ratings == 0].index
    
    # Get predicted ratings for unrated items
    recommendations = []
    for item in unrated_items:
        if item in predicted_ratings_df.columns:
            predicted_rating = predicted_ratings_df.loc[user_id, item]
            recommendations.append((item, predicted_rating))
    
    # Sort by predicted rating
    recommendations.sort(key=lambda x: x[1], reverse=True)
    
    return recommendations[:n_recommendations]

# Function to evaluate SVD model on test set
def evaluate_svd_model(algo, test_user_item_matrix, target_user):
    """Evaluate the SVD model and get recommendations for a target user"""
    try:
        # Make predictions for the test set
        if target_user in test_user_item_matrix.index:
            # Transform the test matrix (but we need to handle the dimension mismatch)
            # For now, let's use the training matrix dimensions
            test_matrix_aligned = test_user_item_matrix.reindex(
                columns=train_user_item_matrix.columns, fill_value=0
            )
            
            # Get SVD recommendations using the aligned test matrix
            svd_recs = get_svd_recommendations(target_user, test_matrix_aligned, algo)
            return svd_recs
        else:
            return []
    except Exception as e:
        print(f"Error in SVD evaluation: {e}")
        return []

# Predict the rating user 1 would give to movie 50
def predict_rating(algo, user_item_matrix, user_id, item_id):
    """Predict rating for a specific user-item pair using trained SVD model"""
    try:
        # Transform the user-item matrix using the trained SVD model
        user_factors = algo.transform(user_item_matrix)
        item_factors = algo.components_
        
        # Reconstruct the ratings matrix
        predicted_ratings = np.dot(user_factors, item_factors)
        predicted_ratings_df = pd.DataFrame(predicted_ratings, 
                                          index=user_item_matrix.index,
                                          columns=user_item_matrix.columns)
        
        # Get the predicted rating for the specific user-item pair
        if user_id in predicted_ratings_df.index and item_id in predicted_ratings_df.columns:
            predicted_rating = predicted_ratings_df.loc[user_id, item_id]
            return predicted_rating
        else:
            return None
    except Exception as e:
        print(f"Error in prediction: {e}")
        return None

if data is not None:
    # Create user-item matrix for evaluation
    print("\nCreating user-item matrix...")
    user_item_matrix = create_user_item_matrix(data)
    print(f"User-item matrix shape: {user_item_matrix.shape}")
    
    # Example: Get recommendations for user 1
    target_user = 1
    print(f"\nGetting recommendations for user {target_user}...")
    
    # User-based collaborative filtering
    print("\n--- User-Based Collaborative Filtering ---")
    try:
        user_based_recs = get_user_based_recommendations(target_user, user_item_matrix)
        print(f"Top 10 recommendations for user {target_user}:")
        for i, (item_id, predicted_rating) in enumerate(user_based_recs, 1):
            print(f"{i}. Item {item_id}: Predicted rating {predicted_rating:.2f}")
    except Exception as e:
        print(f"Error in user-based recommendations: {e}")
    
    # Matrix factorization
    print("\n--- Matrix Factorization (NMF) ---")
    try:
        mf_recs = get_matrix_factorization_recommendations(target_user, user_item_matrix)
        print(f"Top 10 recommendations for user {target_user}:")
        for i, (item_id, predicted_rating) in enumerate(mf_recs, 1):
            print(f"{i}. Item {item_id}: Predicted rating {predicted_rating:.2f}")
    except Exception as e:
        print(f"Error in matrix factorization recommendations: {e}")
    
    # SVD recommendations (using the trained model on test data)
    print("\n--- SVD Recommendations ---")
    try:
        svd_recs = evaluate_svd_model(algo, test_user_item_matrix, target_user)
        if svd_recs:
            print(f"Top 10 recommendations for user {target_user} (from test set):")
            for i, (item_id, predicted_rating) in enumerate(svd_recs, 1):
                print(f"{i}. Item {item_id}: Predicted rating {predicted_rating:.2f}")
        else:
            print(f"No recommendations available for user {target_user} in test set")
    except Exception as e:
        print(f"Error in SVD recommendations: {e}")
    
    # Predict ratings for the test set
    print("\n--- Predicting Ratings for Test Set ---")
    
    def predict_test_ratings(algo, train_matrix, test_data):
        """Predict ratings for all user-item pairs in the test set"""
        predictions = []
        
        # Transform the training matrix to get the latent factors
        user_factors = algo.transform(train_matrix)
        item_factors = algo.components_
        
        # Reconstruct the full ratings matrix
        predicted_ratings = np.dot(user_factors, item_factors)
        predicted_ratings_df = pd.DataFrame(predicted_ratings, 
                                          index=train_matrix.index,
                                          columns=train_matrix.columns)
        
        # Make predictions for each test rating
        for _, row in test_data.iterrows():
            user_id = row['user_id']
            item_id = row['item_id']
            actual_rating = row['rating']
            
            # Check if both user and item exist in our training data
            if user_id in predicted_ratings_df.index and item_id in predicted_ratings_df.columns:
                predicted_rating = predicted_ratings_df.loc[user_id, item_id]
                predictions.append({
                    'user_id': user_id,
                    'item_id': item_id,
                    'actual_rating': actual_rating,
                    'predicted_rating': predicted_rating,
                    'error': abs(actual_rating - predicted_rating)
                })
        
        return predictions
    
    try:
        # Predict ratings for the test set
        predictions = predict_test_ratings(algo, train_user_item_matrix, test_data)
        
        # Show how many predictions were made
        print(f"Total predictions: {len(predictions)}")
        
        # Show some example predictions
        if predictions:
            print("\nExample predictions:")
            for i, pred in enumerate(predictions[:5]):  # Show first 5 predictions
                print(f"{i+1}. User {pred['user_id']}, Item {pred['item_id']}: "
                      f"Actual={pred['actual_rating']}, Predicted={pred['predicted_rating']:.2f}, "
                      f"Error={pred['error']:.2f}")
            
            # Calculate overall accuracy metrics
            errors = [pred['error'] for pred in predictions]
            mae = np.mean(errors)  # Mean Absolute Error
            rmse = np.sqrt(np.mean([pred['error']**2 for pred in predictions]))  # Root Mean Square Error
            
            print(f"\nAccuracy Metrics:")
            print(f"Mean Absolute Error (MAE): {mae:.3f}")
            print(f"Root Mean Square Error (RMSE): {rmse:.3f}")
            
            # Get top 5 recommendations for each user
            print(f"\n--- Top-N Recommendations ---")
            top_n = get_top_n(predictions, n=5)
            
            # Print recommendations for first 3 users
            print(f"Showing top 5 recommendations for first 3 users:")
            for uid, user_ratings in list(top_n.items())[:3]:
                print(f"\nUser {uid} recommendations:")
                for (iid, est_rating) in user_ratings:
                    print(f"\tMovie {iid}: Estimated rating {est_rating:.2f}")
            
            print(f"\nTotal users with recommendations: {len(top_n)}")
        else:
            print("No predictions could be made (no matching users/items in training data)")
    except Exception as e:
        print(f"Error in test set predictions: {e}")
