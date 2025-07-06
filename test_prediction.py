#!/usr/bin/env python3
"""
Test script for rating prediction functionality
"""

import requests
import json

API_BASE_URL = 'http://localhost:5000'

def test_prediction(user_id, item_id, model):
    """Test prediction for a specific user, item, and model"""
    print(f"\n🎯 Testing {model} prediction for User {user_id}, Item {item_id}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/predict?user_id={user_id}&item_id={item_id}&model={model}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"📽️ Movie: {data.get('title', 'Unknown')}")
            print(f"⭐ Predicted Rating: {data.get('predicted_rating', 'N/A')}/5.0")
            print(f"🧠 Model: {data.get('model', 'Unknown')}")
            return True
        else:
            print(f"❌ Error! Status: {response.status_code}")
            print(f"📝 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    """Test all prediction models"""
    print("🎬 Rating Prediction Test Suite")
    print("=" * 50)
    
    # Test parameters
    user_id = 1
    item_id = 100  # Fargo (1996)
    
    models = ['svd', 'nmf', 'content', 'ensemble']
    
    print(f"Testing predictions for User {user_id} and Item {item_id}")
    
    results = {}
    for model in models:
        results[model] = test_prediction(user_id, item_id, model)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    for model, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {model.upper()}: {status}")
    
    print(f"\n🏁 Tests completed. {sum(results.values())}/{len(results)} passed.")

if __name__ == "__main__":
    main()
