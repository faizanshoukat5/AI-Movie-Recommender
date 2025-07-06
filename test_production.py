"""
Comprehensive test suite for the production backend
"""
import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_production import app
from production_rating_db import ProductionRatingDatabase
from config import TestingConfig

@pytest.fixture
def client():
    """Create test client"""
    app.config.from_object(TestingConfig)
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def db():
    """Create test database"""
    test_db = ProductionRatingDatabase(db_path=':memory:')
    return test_db

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'timestamp' in data

def test_home_endpoint(client):
    """Test home endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'message' in data
    assert 'version' in data

def test_status_endpoint(client):
    """Test status endpoint"""
    response = client.get('/status')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'running'
    assert 'version' in data
    assert 'models_trained' in data

def test_movie_search(client):
    """Test movie search endpoint"""
    response = client.get('/movies/search?q=toy')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'movies' in data
    assert 'total' in data
    assert 'query' in data

def test_movie_search_no_query(client):
    """Test movie search without query parameter"""
    response = client.get('/movies/search')
    assert response.status_code == 400
    
    data = json.loads(response.data)
    assert 'error' in data

def test_random_movies(client):
    """Test random movies endpoint"""
    response = client.get('/movies/random?limit=5')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'movies' in data
    assert 'total' in data
    assert len(data['movies']) <= 5

def test_movie_rating_invalid_movie(client):
    """Test rating a non-existent movie"""
    response = client.post('/movies/99999/rate', 
                          json={'user_id': 'test_user', 'rating': 5})
    assert response.status_code == 404

def test_movie_rating_invalid_data(client):
    """Test rating with invalid data"""
    response = client.post('/movies/1/rate', json={})
    assert response.status_code == 400

def test_movie_rating_invalid_rating_value(client):
    """Test rating with invalid rating value"""
    response = client.post('/movies/1/rate', 
                          json={'user_id': 'test_user', 'rating': 10})
    assert response.status_code == 400

def test_recommendations_invalid_user(client):
    """Test recommendations for non-existent user"""
    response = client.get('/recommendations/99999')
    assert response.status_code == 404

def test_database_operations(db):
    """Test database operations"""
    # Test adding a rating
    success = db.add_rating('test_user', 1, 4.5, 'Great movie!')
    assert success == True
    
    # Test getting user ratings
    ratings = db.get_user_ratings('test_user')
    assert len(ratings) == 1
    assert ratings[0]['rating'] == 4.5
    assert ratings[0]['review'] == 'Great movie!'
    
    # Test getting specific rating
    rating = db.get_movie_rating('test_user', 1)
    assert rating == 4.5
    
    # Test getting average rating
    avg_rating, count = db.get_average_rating(1)
    assert avg_rating == 4.5
    assert count == 1
    
    # Test watchlist operations
    success = db.add_to_watchlist('test_user', 1)
    assert success == True
    
    watchlist = db.get_watchlist('test_user')
    assert 1 in watchlist
    
    success = db.remove_from_watchlist('test_user', 1)
    assert success == True
    
    watchlist = db.get_watchlist('test_user')
    assert 1 not in watchlist

def test_database_metadata_operations(db):
    """Test database metadata operations"""
    # Test caching metadata
    metadata = {
        'id': 12345,
        'title': 'Test Movie',
        'poster_path': '/test_poster.jpg',
        'overview': 'A test movie',
        'genres': [{'name': 'Action'}, {'name': 'Comedy'}],
        'credits': {
            'cast': [{'name': 'Actor 1'}, {'name': 'Actor 2'}],
            'crew': [{'job': 'Director', 'name': 'Director 1'}]
        }
    }
    
    success = db.cache_movie_metadata(1, metadata)
    assert success == True
    
    # Test getting cached metadata
    cached = db.get_movie_metadata(1)
    assert cached is not None
    assert cached['title'] == 'Test Movie'
    assert cached['tmdb_id'] == 12345
    assert len(cached['genres']) == 2

def test_database_stats(db):
    """Test database statistics"""
    # Add some test data
    db.add_rating('user1', 1, 4.0)
    db.add_rating('user2', 1, 5.0)
    db.add_rating('user1', 2, 3.0)
    db.add_to_watchlist('user1', 3)
    
    stats = db.get_stats()
    assert stats['total_ratings'] == 3
    assert stats['total_users'] == 2
    assert stats['total_rated_movies'] == 2
    assert stats['total_watchlist_items'] == 1

@patch('app_production.models')
def test_recommendations_with_mock(mock_models, client):
    """Test recommendations with mocked models"""
    # Mock the models
    mock_models.__getitem__.return_value = MagicMock()
    
    # This should not crash even with mocked models
    response = client.get('/recommendations/1')
    # The response will be an error since we don't have real data, but it shouldn't crash
    assert response.status_code in [200, 404]

def test_config_validation():
    """Test configuration validation"""
    from config import ProductionConfig
    
    # Test with default config (should have errors)
    errors = ProductionConfig.validate_config()
    assert len(errors) > 0
    assert any('SECRET_KEY' in error for error in errors)

def test_cache_functionality():
    """Test cache functionality"""
    from app_production import cache_response
    
    # Test cache decorator
    call_count = 0
    
    @cache_response(timeout=1)
    def test_function(x):
        nonlocal call_count
        call_count += 1
        return x * 2
    
    # First call
    result1 = test_function(5)
    assert result1 == 10
    assert call_count == 1
    
    # Second call (should be cached)
    result2 = test_function(5)
    assert result2 == 10
    assert call_count == 1  # Still 1 because it was cached

def test_error_handling(client):
    """Test error handling"""
    # Test 404 errors
    response = client.get('/nonexistent-endpoint')
    assert response.status_code == 404
    
    # Test malformed JSON
    response = client.post('/movies/1/rate', 
                          data='invalid json',
                          content_type='application/json')
    assert response.status_code == 400

def test_cors_headers(client):
    """Test CORS headers"""
    response = client.get('/')
    # Flask-CORS should add these headers
    assert 'Access-Control-Allow-Origin' in response.headers

if __name__ == '__main__':
    """Run tests"""
    pytest.main([__file__, '-v'])
