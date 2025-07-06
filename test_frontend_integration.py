"""
Test script to verify React frontend communication with Flask API
"""
import requests
import json

def test_api_endpoints():
    """Test all API endpoints to ensure they work with the frontend"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing API Endpoints for React Frontend Integration")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Get Users
    print("\n2. Testing Get Users...")
    try:
        response = requests.get(f"{base_url}/users")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Users endpoint works - Found {len(data.get('users', []))} users")
        else:
            print(f"❌ Users endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Users endpoint error: {e}")
    
    # Test 3: Get Items
    print("\n3. Testing Get Items...")
    try:
        response = requests.get(f"{base_url}/items")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Items endpoint works - Found {len(data.get('items', []))} items")
        else:
            print(f"❌ Items endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Items endpoint error: {e}")
    
    # Test 4: Get Recommendations
    print("\n4. Testing Get Recommendations...")
    try:
        response = requests.get(f"{base_url}/recommendations/1")
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get('recommendations', [])
            print(f"✅ Recommendations endpoint works - Got {len(recommendations)} recommendations")
            if recommendations:
                print(f"   First recommendation: Item {recommendations[0]['item_id']} (Rating: {recommendations[0]['predicted_rating']:.2f})")
        else:
            print(f"❌ Recommendations endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Recommendations endpoint error: {e}")
    
    # Test 5: Predict Rating
    print("\n5. Testing Predict Rating...")
    try:
        response = requests.get(f"{base_url}/predict/1/1")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Prediction endpoint works - Predicted rating: {data.get('predicted_rating', 'N/A')}")
        else:
            print(f"❌ Prediction endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Prediction endpoint error: {e}")
    
    # Test 6: CORS Headers
    print("\n6. Testing CORS Headers...")
    try:
        response = requests.options(f"{base_url}/health")
        cors_headers = response.headers.get('Access-Control-Allow-Origin', '')
        if cors_headers:
            print("✅ CORS headers present - React frontend can communicate")
        else:
            print("⚠️ CORS headers may not be properly configured")
    except Exception as e:
        print(f"❌ CORS test error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 API Integration Test Complete!")
    print("💡 If all tests pass, the React frontend should work perfectly!")

if __name__ == "__main__":
    test_api_endpoints()
