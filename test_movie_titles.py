"""
Test script to verify movie titles are included in API responses
"""
import requests
import json

def test_movie_titles():
    """Test that movie titles are properly included in API responses"""
    base_url = "http://localhost:5000"
    
    print("🎬 Testing Movie Titles in API Responses")
    print("=" * 50)
    
    # Test 1: Get Recommendations with Movie Titles
    print("\n1. Testing Recommendations with Movie Titles...")
    try:
        response = requests.get(f"{base_url}/recommendations/1?n=5")
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get('recommendations', [])
            print(f"✅ Got {len(recommendations)} recommendations")
            
            if recommendations:
                first_rec = recommendations[0]
                movie_title = first_rec.get('movie_title', 'N/A')
                item_id = first_rec.get('item_id', 'N/A')
                rating = first_rec.get('predicted_rating', 'N/A')
                
                print(f"   🎭 First recommendation:")
                print(f"      Title: {movie_title}")
                print(f"      ID: {item_id}")
                print(f"      Rating: {rating:.2f}")
                
                # Show all top 5 recommendations
                print(f"\n   📽️  Top 5 Movie Recommendations:")
                for i, rec in enumerate(recommendations[:5], 1):
                    title = rec.get('movie_title', f"Movie {rec.get('item_id', 'N/A')}")
                    rating = rec.get('predicted_rating', 0)
                    print(f"      {i}. {title} - {rating:.2f}⭐")
        else:
            print(f"❌ Recommendations failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Recommendations error: {e}")
    
    # Test 2: Rating Prediction with Movie Title
    print("\n2. Testing Rating Prediction with Movie Title...")
    try:
        response = requests.get(f"{base_url}/predict/1/1")
        if response.status_code == 200:
            data = response.json()
            movie_title = data.get('movie_title', 'N/A')
            item_id = data.get('item_id', 'N/A')
            predicted_rating = data.get('predicted_rating', 'N/A')
            actual_rating = data.get('actual_rating', 'N/A')
            
            print(f"✅ Prediction successful")
            print(f"   🎭 Movie: {movie_title}")
            print(f"   🎯 Predicted Rating: {predicted_rating:.2f}")
            print(f"   ⭐ Actual Rating: {actual_rating if actual_rating != 'N/A' else 'Not rated'}")
        else:
            print(f"❌ Prediction failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Prediction error: {e}")
    
    # Test 3: Test some famous movies
    print("\n3. Testing Famous Movies...")
    famous_movie_ids = [1, 50, 100, 200, 300]  # Common movie IDs
    
    for movie_id in famous_movie_ids:
        try:
            response = requests.get(f"{base_url}/predict/1/{movie_id}")
            if response.status_code == 200:
                data = response.json()
                movie_title = data.get('movie_title', f'Movie {movie_id}')
                predicted_rating = data.get('predicted_rating', 0)
                print(f"   🎬 {movie_title} - Predicted: {predicted_rating:.2f}⭐")
            else:
                print(f"   ❌ Movie {movie_id} failed")
        except Exception as e:
            print(f"   ❌ Movie {movie_id} error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Movie Titles Test Complete!")
    print("🎭 Movie titles should now be displayed in the React frontend!")

if __name__ == "__main__":
    test_movie_titles()
