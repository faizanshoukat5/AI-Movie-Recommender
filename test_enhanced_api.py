#!/usr/bin/env python3
"""
Test script for the AI Movie Recommendation Engine
Tests all the new multi-model functionality
"""

import requests
import json
import time

API_BASE_URL = 'http://localhost:5000'

def test_endpoint(endpoint, description):
    """Test a specific endpoint"""
    print(f"\n🧪 Testing {description}...")
    print(f"📍 Endpoint: {endpoint}")
    
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Status: {response.status_code}")
            print(f"📊 Response keys: {list(data.keys())}")
            return data
        else:
            print(f"❌ Error! Status: {response.status_code}")
            print(f"📝 Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def main():
    """Main test function"""
    print("🎬 AI Movie Recommendation Engine - API Test Suite")
    print("=" * 60)
    
    # Test 1: Basic API health
    test_endpoint("/", "API Health Check")
    
    # Test 2: Available models
    models_data = test_endpoint("/models", "Available Models")
    if models_data:
        print(f"🧠 Available models: {models_data.get('available_models', [])}")
    
    # Test 3: Movie search
    search_data = test_endpoint("/search?q=star&limit=3", "Movie Search")
    if search_data:
        print(f"🔍 Found {len(search_data.get('movies', []))} movies")
    
    # Test 4: Random movies
    random_data = test_endpoint("/movies/random?limit=5", "Random Movies")
    if random_data:
        print(f"🎲 Got {len(random_data.get('movies', []))} random movies")
    
    # Test 5: SVD Recommendations
    svd_data = test_endpoint("/recommendations/1?n=3&model=svd", "SVD Recommendations")
    if svd_data:
        print(f"🎯 SVD recommendations: {len(svd_data.get('recommendations', []))}")
    
    # Test 6: Ensemble Recommendations
    ensemble_data = test_endpoint("/recommendations/1?n=3&model=ensemble", "Ensemble Recommendations")
    if ensemble_data:
        print(f"🎯 Ensemble recommendations: {len(ensemble_data.get('recommendations', []))}")
    
    # Test 7: Model Comparison
    comparison_data = test_endpoint("/compare/1?n=2", "Model Comparison")
    if comparison_data:
        print(f"⚖️ Model comparison data available for user {comparison_data.get('user_id')}")
        comparison = comparison_data.get('comparison', {})
        for model, results in comparison.items():
            if isinstance(results, list):
                print(f"   {model}: {len(results)} recommendations")
            else:
                print(f"   {model}: {results}")
    
    # Test 8: Rating Prediction
    prediction_data = test_endpoint("/predict?user_id=1&item_id=100&model=svd", "Rating Prediction")
    if prediction_data:
        print(f"⭐ Predicted rating: {prediction_data.get('predicted_rating')}")
    
    # Test 9: System Status
    status_data = test_endpoint("/status", "System Status")
    if status_data:
        print(f"📊 System status: {status_data.get('status')}")
        print(f"🎬 Total movies: {status_data.get('total_movies')}")
        print(f"👥 Total users: {status_data.get('total_users')}")
    
    print("\n" + "=" * 60)
    print("🏁 Test Suite Complete!")

if __name__ == "__main__":
    main()
