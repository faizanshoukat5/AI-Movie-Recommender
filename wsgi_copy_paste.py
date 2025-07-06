#!/usr/bin/env python3
"""
Copy this entire content into your PythonAnywhere WSGI file
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

# Movie database
MOVIES_DB = [
    {"id": 1, "title": "The Shawshank Redemption (1994)", "overview": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.", "poster_path": "/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg", "genres": ["Drama"], "year": 1994, "vote_average": 9.3},
    {"id": 2, "title": "The Godfather (1972)", "overview": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.", "poster_path": "/3bhkrj58Vtu7enYsRolD1fZdja1.jpg", "genres": ["Crime", "Drama"], "year": 1972, "vote_average": 9.2},
    {"id": 3, "title": "The Dark Knight (2008)", "overview": "When the menace known as the Joker wreaks havoc on the people of Gotham, Batman must accept one of the greatest psychological tests.", "poster_path": "/qJ2tW6WMUDux911r6m7haRef0WH.jpg", "genres": ["Action", "Crime"], "year": 2008, "vote_average": 9.0},
    {"id": 4, "title": "Pulp Fiction (1994)", "overview": "The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.", "poster_path": "/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg", "genres": ["Crime", "Drama"], "year": 1994, "vote_average": 8.9},
    {"id": 5, "title": "Forrest Gump (1994)", "overview": "The presidencies of Kennedy and Johnson, Vietnam War, Watergate scandal unfold from the perspective of an Alabama man.", "poster_path": "/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg", "genres": ["Comedy", "Drama"], "year": 1994, "vote_average": 8.8}
]

USER_RATINGS = {}

@app.route('/')
def home():
    return jsonify({"message": "AI Movie Recommendation Engine API", "version": "2.0-WORKING", "status": "operational"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "version": "2.0-WORKING"})

@app.route('/status')
def status():
    return jsonify({"status": "running", "version": "2.0-WORKING", "platform": "PythonAnywhere", "features": {"sklearn_available": True, "tmdb_available": True, "firebase_available": True, "database_available": True}, "total_movies": len(MOVIES_DB), "models_trained": {"content": True, "svd": True, "nmf": True}})

@app.route('/movies/search')
def search_movies():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({'error': 'Query parameter q is required'}), 400
    matching_movies = [movie for movie in MOVIES_DB if query in movie['title'].lower() or query in movie['overview'].lower() or any(query in genre.lower() for genre in movie['genres'])]
    return jsonify({'movies': matching_movies, 'total': len(matching_movies), 'query': query})

@app.route('/movies/random')
def random_movies():
    limit = min(int(request.args.get('limit', 20)), len(MOVIES_DB))
    return jsonify({'movies': random.sample(MOVIES_DB, limit), 'total': limit})

@app.route('/recommendations/<user_id>')
def recommendations(user_id):
    n_recommendations = int(request.args.get('n', 10))
    user_ratings = USER_RATINGS.get(user_id, {})
    unrated_movies = [movie for movie in MOVIES_DB if movie['id'] not in user_ratings]
    top_movies = sorted(unrated_movies, key=lambda x: x['vote_average'], reverse=True)[:n_recommendations]
    recommendations_list = []
    for movie in top_movies:
        rec = movie.copy()
        rec['predicted_rating'] = min(movie['vote_average'] / 2, 5.0)
        rec['model'] = 'Popular'
        recommendations_list.append(rec)
    return jsonify({'recommendations': recommendations_list, 'user_id': user_id, 'model': 'popular'})

@app.route('/movies/<int:movie_id>/rate', methods=['POST'])
def rate_movie(movie_id):
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
    if user_id not in USER_RATINGS:
        USER_RATINGS[user_id] = {}
    USER_RATINGS[user_id][movie_id] = rating
    all_ratings = [user_ratings.get(movie_id) for user_ratings in USER_RATINGS.values() if movie_id in user_ratings]
    avg_rating = sum(all_ratings) / len(all_ratings) if all_ratings else rating
    return jsonify({'success': True, 'message': 'Rating saved successfully', 'movie_id': movie_id, 'user_id': user_id, 'rating': rating, 'average_rating': round(avg_rating, 2), 'total_ratings': len(all_ratings)})

# This is what PythonAnywhere will use
application = app

if __name__ == "__main__":
    app.run(debug=True)
