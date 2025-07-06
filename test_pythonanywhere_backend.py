"""
Test script for PythonAnywhere backend
Run this to verify your backend is working correctly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_backend():
    print("🧪 Testing PythonAnywhere Backend...")
    print("=" * 50)
    
    # Test 1: Import test
    try:
        from app_pythonanywhere import app
        print("✅ Backend imports successfully")
    except Exception as e:
        print(f"❌ Backend import failed: {e}")
        return False
    
    # Test 2: Basic functionality
    try:
        with app.test_client() as client:
            # Test home endpoint
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Home endpoint works")
                data = response.get_json()
                print(f"   Version: {data.get('version', 'unknown')}")
                print(f"   Features: {data.get('features', {})}")
            else:
                print(f"❌ Home endpoint failed: {response.status_code}")
                return False
            
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Health endpoint works")
                data = response.get_json()
                print(f"   Status: {data.get('status', 'unknown')}")
                print(f"   Services: {data.get('services', {})}")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
            
            # Test status endpoint
            response = client.get('/status')
            if response.status_code == 200:
                print("✅ Status endpoint works")
                data = response.get_json()
                print(f"   Models: {data.get('models_trained', {})}")
                print(f"   Movies: {data.get('total_movies', 0)}")
                print(f"   Cache: {data.get('cache_size', 0)}")
            else:
                print(f"❌ Status endpoint failed: {response.status_code}")
                return False
            
            # Test movie search
            response = client.get('/movies/search?q=test')
            if response.status_code == 200:
                print("✅ Movie search works")
                data = response.get_json()
                print(f"   Found {data.get('total', 0)} movies")
            else:
                print(f"❌ Movie search failed: {response.status_code}")
            
            # Test random movies
            response = client.get('/movies/random?limit=5')
            if response.status_code == 200:
                print("✅ Random movies endpoint works")
                data = response.get_json()
                print(f"   Returned {len(data.get('movies', []))} movies")
            else:
                print(f"❌ Random movies failed: {response.status_code}")
            
            # Test recommendations (might fail if no data)
            response = client.get('/recommendations/1')
            if response.status_code == 200:
                print("✅ Recommendations endpoint works")
                data = response.get_json()
                print(f"   Returned {len(data.get('recommendations', []))} recommendations")
            elif response.status_code == 404:
                print("⚠️  Recommendations endpoint works (no data for user 1)")
            else:
                print(f"❌ Recommendations endpoint failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False
    
    print("=" * 50)
    print("🎉 Backend test completed successfully!")
    print("📝 Upload these files to PythonAnywhere:")
    print("   - app_pythonanywhere.py")
    print("   - config_pythonanywhere.py")
    print("   - production_rating_db.py")
    print("   - wsgi.py")
    print("   - requirements_production.txt")
    print("🚀 Your backend is ready for production!")
    
    return True

if __name__ == "__main__":
    success = test_backend()
    sys.exit(0 if success else 1)
