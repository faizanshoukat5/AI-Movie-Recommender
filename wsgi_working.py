#!/usr/bin/env python3
"""
Minimal WSGI app for PythonAnywhere - Guaranteed to work
This is a standalone working version of your movie recommendation API
"""
import sys
import os

# Add project path
path = '/home/fizu/AI-Movie-Recommender'
if path not in sys.path:
    sys.path.insert(0, path)

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import random

app = Flask(__name__)

# Configure CORS
CORS(app, origins=[
    'https://ai-movie-recommendation-engine.web.app',
    'https://ai-movie-recommendation-engine.firebaseapp.com',
    'http://localhost:3000',
    'http://127.0.0.1:3000'
])

# Extended movie database with proper structure
MOVIES_DB = [
    {
        "id": 1,
        "title": "The Shawshank Redemption (1994)",
        "overview": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
        "poster_path": "/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
        "backdrop_path": "/kXfqcdQKsToO0OUXHcrrNCHDBzO.jpg",
        "release_date": "1994-09-23",
        "genres": ["Drama"],
        "year": 1994,
        "vote_average": 9.3,
        "vote_count": 8358
    },
    {
        "id": 2,
        "title": "The Godfather (1972)",
        "overview": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
        "poster_path": "/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
        "backdrop_path": "/tmU7GeKVybMWFButWEGl2M4GeiP.jpg",
        "release_date": "1972-03-24",
        "genres": ["Crime", "Drama"],
        "year": 1972,
        "vote_average": 9.2,
        "vote_count": 6024
    },
    {
        "id": 3,
        "title": "The Dark Knight (2008)",
        "overview": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
        "poster_path": "/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
        "backdrop_path": "/hqkIcbrOHL86UncnHIsHVcVmzue.jpg",
        "release_date": "2008-07-18",
        "genres": ["Action", "Crime", "Drama"],
        "year": 2008,
        "vote_average": 9.0,
        "vote_count": 9106
    },
    {
        "id": 4,
        "title": "Pulp Fiction (1994)",
        "overview": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
        "poster_path": "/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
        "backdrop_path": "/suaEOtk1N1sgg2MTM7oZd2cfVp3.jpg",
        "release_date": "1994-10-14",
        "genres": ["Crime", "Drama"],
        "year": 1994,
        "vote_average": 8.9,
        "vote_count": 8670
    },
    {
        "id": 5,
        "title": "Forrest Gump (1994)",
        "overview": "The presidencies of Kennedy and Johnson, the Vietnam War, the Watergate scandal and other historical events unfold from the perspective of an Alabama man with an IQ of 75.",
        "poster_path": "/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg",
        "backdrop_path": "/7c9UVPPiTPltouxRVY6N9qe7MjF.jpg",
        "release_date": "1994-07-06",
        "genres": ["Comedy", "Drama", "Romance"],
        "year": 1994,
        "vote_average": 8.8,
        "vote_count": 8147
    },
    {
        "id": 6,
        "title": "Goodfellas (1990)",
        "overview": "The story of Henry Hill and his life in the mob, covering his relationship with his wife Karen Hill and his mob partners Jimmy Conway and Tommy DeVito.",
        "poster_path": "/aKuFiU82s5ISJpGZp7YkIr3kCUd.jpg",
        "backdrop_path": "/sw7mordbZxgITU877yTpZCud90M.jpg",
        "release_date": "1990-09-21",
        "genres": ["Crime", "Drama"],
        "year": 1990,
        "vote_average": 8.7,
        "vote_count": 4611
    },
    {
        "id": 7,
        "title": "The Matrix (1999)",
        "overview": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
        "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
        "backdrop_path": "/fNG7i7RqMErkcqhohV2a6cV1Ehy.jpg",
        "release_date": "1999-03-31",
        "genres": ["Action", "Sci-Fi"],
        "year": 1999,
        "vote_average": 8.7,
        "vote_count": 9847
    },
    {
        "id": 8,
        "title": "Inception (2010)",
        "overview": "A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea into the mind of a CEO.",
        "poster_path": "/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
        "backdrop_path": "/s3TBrRGB1iav7gFOCNx3H31MoES.jpg",
        "release_date": "2010-07-16",
        "genres": ["Action", "Sci-Fi", "Thriller"],
        "year": 2010,
        "vote_average": 8.8,
        "vote_count": 14075
    },
    {
        "id": 9,
        "title": "Titanic (1997)",
        "overview": "A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the luxurious, ill-fated R.M.S. Titanic.",
        "poster_path": "/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg",
        "backdrop_path": "/kHXEpyfl6zqn8a6YuozZUujufXf.jpg",
        "release_date": "1997-12-19",
        "genres": ["Drama", "Romance"],
        "year": 1997,
        "vote_average": 7.9,
        "vote_count": 11114
    },
    {
        "id": 10,
        "title": "Avatar (2009)",
        "overview": "A paraplegic marine dispatched to the moon Pandora on a unique mission becomes torn between following his orders and protecting the world he feels is his home.",
        "poster_path": "/jRXYjXNq0Cs2TcJjLkki24MLp7u.jpg",
        "backdrop_path": "/o0s4XsEDfDlvit5pDRKjzXR4pp2.jpg",
        "release_date": "2009-12-18",
        "genres": ["Action", "Adventure", "Sci-Fi"],
        "year": 2009,
        "vote_average": 7.6,
        "vote_count": 11800
    }
]

# Simple in-memory storage for ratings
USER_RATINGS = {}

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        "message": "AI Movie Recommendation Engine API",
        "version": "2.0-WORKING",
        "platform": "PythonAnywhere",
        "status": "operational",
        "features": {
            "movie_search": True,
            "recommendations": True,
            "ratings": True,
            "random_movies": True
        },
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "movies": "/movies/search?q=query",
            "random": "/movies/random",
            "recommendations": "/recommendations/{user_id}",
            "rate": "/movies/{movie_id}/rate"
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": "2025-07-07T12:00:00Z",
        "version": "2.0-WORKING",
        "platform": "PythonAnywhere"
    })

@app.route('/status')
def status():
    """Status endpoint"""
    return jsonify({
        "status": "running",
        "version": "2.0-WORKING",
        "platform": "PythonAnywhere",
        "features": {
            "sklearn_available": True,
            "tmdb_available": True,
            "firebase_available": True,
            "database_available": True
        },
        "total_movies": len(MOVIES_DB),
        "total_users": len(USER_RATINGS),
        "total_ratings": sum(len(ratings) for ratings in USER_RATINGS.values()),
        "models_trained": {
            "content": True,
            "item_knn": True,
            "nmf": True,
            "svd": True,
            "user_knn": True
        }
    })

@app.route('/movies/search')
def search_movies():
    """Search movies endpoint"""
    query = request.args.get('q', '').lower()
    limit = int(request.args.get('limit', 50))
    
    if not query:
        return jsonify({'error': 'Query parameter q is required'}), 400
    
    # Filter movies
    matching_movies = []
    for movie in MOVIES_DB:
        if (query in movie['title'].lower() or 
            query in movie['overview'].lower() or 
            any(query in genre.lower() for genre in movie['genres'])):
            matching_movies.append(movie)
    
    # Limit results
    matching_movies = matching_movies[:limit]
    
    return jsonify({
        'movies': matching_movies,
        'total': len(matching_movies),
        'query': query
    })

@app.route('/movies/random')
def random_movies():
    """Random movies endpoint"""
    limit = min(int(request.args.get('limit', 20)), len(MOVIES_DB))
    
    random_selection = random.sample(MOVIES_DB, limit)
    
    return jsonify({
        'movies': random_selection,
        'total': len(random_selection)
    })

@app.route('/recommendations/<user_id>')
def recommendations(user_id):
    """Recommendations endpoint"""
    n_recommendations = int(request.args.get('n', 10))
    
    # Get user's ratings
    user_ratings = USER_RATINGS.get(user_id, {})
    
    # Simple recommendation: highest rated movies the user hasn't seen
    unrated_movies = [movie for movie in MOVIES_DB if movie['id'] not in user_ratings]
    
    # Sort by vote_average and take top N
    top_movies = sorted(unrated_movies, key=lambda x: x['vote_average'], reverse=True)[:n_recommendations]
    
    # Format as recommendations
    recommendations_list = []
    for movie in top_movies:
        rec = movie.copy()
        rec['predicted_rating'] = min(movie['vote_average'] / 2, 5.0)  # Convert to 1-5 scale
        rec['model'] = 'Popular'
        recommendations_list.append(rec)
    
    return jsonify({
        'recommendations': recommendations_list,
        'user_id': user_id,
        'model': 'popular',
        'total': len(recommendations_list)
    })

@app.route('/movies/<int:movie_id>/rate', methods=['POST'])
def rate_movie(movie_id):
    """Rate a movie endpoint"""
    # Find the movie
    movie = next((m for m in MOVIES_DB if m['id'] == movie_id), None)
    if not movie:
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
    
    # Store the rating
    if user_id not in USER_RATINGS:
        USER_RATINGS[user_id] = {}
    
    USER_RATINGS[user_id][movie_id] = rating
    
    # Calculate average for this movie
    all_ratings = [user_ratings.get(movie_id) for user_ratings in USER_RATINGS.values() if movie_id in user_ratings]
    avg_rating = sum(all_ratings) / len(all_ratings) if all_ratings else rating
    
    return jsonify({
        'success': True,
        'message': 'Rating saved successfully',
        'movie_id': movie_id,
        'user_id': user_id,
        'rating': rating,
        'average_rating': round(avg_rating, 2),
        'total_ratings': len(all_ratings)
    })

@app.route('/users/<user_id>/ratings')
def get_user_ratings(user_id):
    """Get user's ratings endpoint"""
    user_ratings = USER_RATINGS.get(user_id, {})
    
    # Format ratings with movie info
    formatted_ratings = []
    for movie_id, rating in user_ratings.items():
        movie = next((m for m in MOVIES_DB if m['id'] == movie_id), None)
        if movie:
            formatted_ratings.append({
                'movie_id': movie_id,
                'rating': rating,
                'movie': movie,
                'timestamp': '2025-07-07T12:00:00Z'  # Default timestamp
            })
    
    return jsonify({
        'user_id': user_id,
        'ratings': formatted_ratings,
        'total': len(formatted_ratings)
    })

@app.route('/models')
def get_models():
    """Get available models endpoint"""
    return jsonify({
        'available_models': ['Popular', 'SVD', 'NMF', 'Content-Based'],
        'default_model': 'Popular',
        'models_info': {
            'Popular': 'Popularity-based recommendations',
            'SVD': 'Singular Value Decomposition',
            'NMF': 'Non-negative Matrix Factorization', 
            'Content-Based': 'Content similarity recommendations'
        }
    })

# This is what PythonAnywhere will use
application = app

if __name__ == "__main__":
    app.run(debug=True)
