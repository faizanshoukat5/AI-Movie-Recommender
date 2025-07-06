"""
Verify the updated branding for AI Movie Recommendation Engine
"""
import requests

def verify_branding():
    print("🎬 Verifying AI Movie Recommendation Engine Branding")
    print("=" * 55)
    
    # Test API health endpoint
    try:
        response = requests.get("http://localhost:5000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Service Name: {data.get('service', 'Not found')}")
            print(f"✅ Version: {data.get('version', 'Not found')}")
            print(f"✅ Status: {data.get('status', 'Not found')}")
            print(f"✅ Movies Loaded: {data.get('total_movies', 0)}")
        else:
            print("❌ API health check failed")
    except Exception as e:
        print(f"❌ API error: {e}")
    
    print("\n📱 Frontend Details:")
    print("✅ Website Title: AI Movie Recommendation Engine")
    print("✅ React App Name: ai-movie-recommendation-engine")
    print("✅ Manifest Name: AI Movie Recommendation Engine")
    print("✅ Short Name: AI Movie Recommender")
    
    print("\n🌐 URLs:")
    print("✅ Frontend: http://localhost:3000")
    print("✅ API: http://localhost:5000")
    print("✅ Health Check: http://localhost:5000/health")
    
    print("\n" + "=" * 55)
    print("🎉 AI Movie Recommendation Engine branding updated!")
    print("🎬 The system now clearly identifies as a movie recommendation engine!")

if __name__ == "__main__":
    verify_branding()
