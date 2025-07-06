import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:5000"

def test_api():
    """Test all API endpoints"""
    
    print("🚀 Testing AI Recommendation Engine API")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Health Check:")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Get recommendations for user 1 (SVD)
    print("\n2. Get SVD Recommendations for User 1:")
    try:
        response = requests.get(f"{BASE_URL}/recommendations/1?n=5&algorithm=svd")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Get collaborative filtering recommendations for user 1
    print("\n3. Get Collaborative Filtering Recommendations for User 1:")
    try:
        response = requests.get(f"{BASE_URL}/recommendations/1?n=5&algorithm=collaborative")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Predict rating for user 1, item 50
    print("\n4. Predict Rating for User 1, Item 50:")
    try:
        response = requests.get(f"{BASE_URL}/predict/1/50")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Get available users (first 10)
    print("\n5. Get Available Users (showing count only):")
    try:
        response = requests.get(f"{BASE_URL}/users")
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Total Users: {data['count']}")
        print(f"First 10 Users: {data['users'][:10]}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 6: Get available items (first 10)
    print("\n6. Get Available Items (showing count only):")
    try:
        response = requests.get(f"{BASE_URL}/items")
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Total Items: {data['count']}")
        print(f"First 10 Items: {data['items'][:10]}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 7: Error handling - non-existent user
    print("\n7. Error Handling - Non-existent User:")
    try:
        response = requests.get(f"{BASE_URL}/recommendations/9999")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ API Testing Complete!")
    print("\nYour AI Recommendation Engine API is now ready for production!")
    print("\nExample API calls:")
    print("- Get 10 SVD recommendations: GET /recommendations/1?n=10&algorithm=svd")
    print("- Get 5 collaborative recommendations: GET /recommendations/1?n=5&algorithm=collaborative")
    print("- Predict specific rating: GET /predict/1/50")
    print("- Health check: GET /health")

if __name__ == "__main__":
    # Wait a moment for server to be ready
    import time
    time.sleep(2)
    test_api()
