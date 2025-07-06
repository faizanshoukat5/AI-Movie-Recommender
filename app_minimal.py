#!/usr/bin/env python3
"""
Minimal working Flask app for PythonAnywhere
Use this as a fallback if the main app fails to load
"""
import sys
import os

# Add project path
project_path = '/home/fizu/AI-Movie-Recommender'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

from flask import Flask, jsonify, request
from flask_cors import CORS
import json

app = Flask(__name__)

# Configure CORS
CORS(app, origins=[
    'https://ai-movie-recommendation-engine.web.app',
    'https://ai-movie-recommendation-engine.firebaseapp.com',
    'http://localhost:3000'
])

# Simple movie data for testing
SAMPLE_MOVIES = [
    {
        'id': 1,
        'title': 'The Shawshank Redemption (1994)',
        'overview': 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.',
        'poster_path': '/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg',
        'genres': ['Drama'],
        'year': 1994,
        'vote_average': 9.3,
        'vote_count': 8358
    },
    {
        'id': 2,
        'title': 'The Godfather (1972)',
        'overview': 'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.',
        'poster_path': '/3bhkrj58Vtu7enYsRolD1fZdja1.jpg',
        'genres': ['Crime', 'Drama'],
        'year': 1972,
        'vote_average': 9.2,
        'vote_count': 6024
    },
    {
        'id': 3,
        'title': 'The Dark Knight (2008)',
        'overview': 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.',
        'poster_path': '/qJ2tW6WMUDux911r6m7haRef0WH.jpg',
        'genres': ['Action', 'Crime', 'Drama'],
        'year': 2008,
        'vote_average': 9.0,
        'vote_count': 9106
    },
    {
        'id': 4,
        'title': 'Pulp Fiction (1994)',
        'overview': 'The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.',
        'poster_path': '/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg',
        'genres': ['Crime', 'Drama'],
        'year': 1994,
        'vote_average': 8.9,
        'vote_count': 8670
    },
    {
        'id': 5,
        'title': 'Forrest Gump (1994)',
        'overview': 'The presidencies of Kennedy and Johnson, the Vietnam War, the Watergate scandal and other historical events unfold from the perspective of an Alabama man with an IQ of 75.',
        'poster_path': '/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg',
        'genres': ['Comedy', 'Drama', 'Romance'],
        'year': 1994,
        'vote_average': 8.8,
        'vote_count': 8147
    }
]

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        "message": "AI Movie Recommendation Engine API - Minimal Version",
        "version": "1.0-MINIMAL",
        "status": "working",
        "note": "This is a minimal version for testing. Main app failed to load.",
        "endpoints": {
            "health": "/health",
            "movies": "/movies/search?q=query",
            "status": "/status"
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "minimal",
        "timestamp": "2025-07-07T12:00:00Z"
    })

@app.route('/status')
def status():
    """Status endpoint"""
    return jsonify({
        "status": "running",
        "version": "1.0-MINIMAL",
        "platform": "PythonAnywhere",
        "features": {
            "sklearn_available": False,
            "tmdb_available": False,
            "firebase_available": False,
            "database_available": False
        },
        "total_movies": len(SAMPLE_MOVIES),
        "note": "Minimal version for testing"
    })

@app.route('/movies/search')
def search_movies():
    """Search movies endpoint"""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({'error': 'Query parameter q is required'}), 400
    
    # Filter sample movies
    matching_movies = []
    for movie in SAMPLE_MOVIES:
        if query in movie['title'].lower() or query in ' '.join(movie['genres']).lower():
            matching_movies.append(movie)
    
    return jsonify({
        'movies': matching_movies,
        'total': len(matching_movies),
        'query': query
    })

@app.route('/movies/random')
def random_movies():
    """Random movies endpoint"""
    limit = min(int(request.args.get('limit', 5)), len(SAMPLE_MOVIES))
    
    return jsonify({
        'movies': SAMPLE_MOVIES[:limit],
        'total': limit
    })

@app.route('/recommendations/<int:user_id>')
def recommendations(user_id):
    """Simple recommendations endpoint"""
    # Return top-rated movies as recommendations
    recommendations = []
    for movie in SAMPLE_MOVIES[:3]:
        rec = movie.copy()
        rec['predicted_rating'] = movie['vote_average'] / 2  # Convert to 1-5 scale
        rec['model'] = 'Popular'
        recommendations.append(rec)
    
    return jsonify({
        'recommendations': recommendations,
        'user_id': user_id,
        'model': 'popular'
    })

@app.route('/debug')
def debug():
    """Debug endpoint"""
    return jsonify({
        "python_version": sys.version,
        "python_path": sys.path,
        "current_directory": os.getcwd(),
        "environment": dict(os.environ),
        "flask_working": True
    })

# This is what PythonAnywhere will use
application = app

if __name__ == "__main__":
    app.run(debug=True)
