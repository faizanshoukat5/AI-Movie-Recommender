#!/usr/bin/env python3
"""
Test script to verify all enhanced features of the AI Movie Recommendation Engine
"""

import requests
import json
from datetime import datetime

API_BASE_URL = "http://localhost:5000"

def test_api_endpoint(endpoint, method="GET", data=None, expected_status=200):
    """Test an API endpoint and return the result"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        if response.status_code == expected_status:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"Status {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    print("🎬 AI Movie Recommendation Engine - Feature Test Suite")
    print("=" * 60)
    print(f"Testing API at: {API_BASE_URL}")
    print(f"Test run: {datetime.now()}")
    print("=" * 60)
    
    tests = [
        # Core endpoints
        ("GET /movies (basic)", "/movies?limit=3", "GET"),
        ("GET /movies (with posters)", "/movies?limit=3&include_posters=true", "GET"),
        ("GET /search", "/search?q=star&include_posters=true", "GET"),
        ("GET /recommendations", "/recommendations/1", "GET"),
        ("GET /status", "/status", "GET"),
        
        # Enhanced movie details
        ("GET /movies/1/enhanced", "/movies/1/enhanced", "GET"),
        
        # Rating system
        ("POST /movies/1/rate", "/movies/1/rate", "POST", {"rating": 5, "user_id": 1}),
        ("GET /users/1/ratings", "/users/1/ratings", "GET"),
        ("GET /movies/1/rating/1", "/movies/1/rating/1", "GET"),
        
        # Watchlist
        ("POST /users/1/watchlist/2", "/users/1/watchlist/2", "POST", {"user_id": 1}),
        ("GET /users/1/watchlist", "/users/1/watchlist", "GET"),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, endpoint, method, *args in tests:
        data = args[0] if args else None
        print(f"\n🔍 Testing: {test_name}")
        result = test_api_endpoint(endpoint, method, data)
        
        if result["success"]:
            print(f"✅ PASSED")
            if "movies" in result["data"]:
                movies = result["data"]["movies"]
                if movies and isinstance(movies, list):
                    movie = movies[0]
                    if "poster_url" in movie:
                        print(f"   📸 Poster: {movie['poster_url'][:50]}...")
                    if "title" in movie:
                        print(f"   🎬 Title: {movie['title']}")
            elif "message" in result["data"]:
                print(f"   💬 Message: {result['data']['message']}")
            passed += 1
        else:
            print(f"❌ FAILED: {result['error']}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Your AI Movie Recommendation Engine is ready!")
    else:
        print("⚠️  Some tests failed. Please check the server and try again.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
