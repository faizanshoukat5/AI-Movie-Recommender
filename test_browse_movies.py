"""
Test the Browse Movies functionality
"""
import requests

def test_browse_movies():
    base_url = "http://localhost:5000"
    
    print("🎬 Testing Browse Movies Functionality")
    print("=" * 40)
    
    # Test random movies
    print("\n1. Testing Random Movies:")
    try:
        response = requests.get(f"{base_url}/movies/random")
        if response.status_code == 200:
            data = response.json()
            movies = data.get('movies', [])
            print(f"✅ Random movies loaded: {len(movies)}")
            for i, movie in enumerate(movies[:3], 1):
                print(f"   {i}. {movie['movie_title']}")
        else:
            print(f"❌ Random movies failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Random movies error: {e}")
    
    # Test search functionality
    print("\n2. Testing Movie Search:")
    search_terms = ["star", "love", "batman", "toy"]
    
    for term in search_terms:
        try:
            response = requests.get(f"{base_url}/movies/search?q={term}")
            if response.status_code == 200:
                data = response.json()
                movies = data.get('movies', [])
                print(f"✅ '{term}' search: {len(movies)} results")
                if movies:
                    print(f"   First result: {movies[0]['movie_title']}")
            else:
                print(f"❌ '{term}' search failed: {response.status_code}")
        except Exception as e:
            print(f"❌ '{term}' search error: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 Browse Movies test complete!")
    print("🌐 The search button should now work in the React frontend!")

if __name__ == "__main__":
    test_browse_movies()
