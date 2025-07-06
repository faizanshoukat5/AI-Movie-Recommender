#!/usr/bin/env python3
"""
Full System Test for AI Movie Recommendation Engine
Tests both PythonAnywhere backend and Firebase frontend integration
"""
import requests
import json
import time
from datetime import datetime

class FullSystemTest:
    def __init__(self):
        self.backend_url = "https://fizu.pythonanywhere.com"
        self.frontend_url = "https://ai-movie-recommendation-engine.web.app"
        self.test_results = []
        
    def log_result(self, test_name, success, message, response_data=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        if response_data:
            result["data"] = response_data
        self.test_results.append(result)
        print(f"{status} - {test_name}: {message}")
        
    def test_backend_health(self):
        """Test backend health and basic connectivity"""
        print("\n🔍 Testing Backend Health...")
        
        try:
            # Test root endpoint
            response = requests.get(f"{self.backend_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "AI Movie Recommendation Engine" in data.get("message", ""):
                    self.log_result("Backend Root", True, "API root endpoint working")
                else:
                    self.log_result("Backend Root", False, f"Unexpected response: {data}")
            else:
                self.log_result("Backend Root", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("Backend Root", False, f"Connection error: {str(e)}")
            
        try:
            # Test health endpoint
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_result("Backend Health", True, "Health endpoint working")
                else:
                    self.log_result("Backend Health", False, f"Unhealthy status: {data}")
            else:
                self.log_result("Backend Health", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("Backend Health", False, f"Health check failed: {str(e)}")
            
    def test_backend_status(self):
        """Test backend status and feature availability"""
        print("\n🔍 Testing Backend Status...")
        
        try:
            response = requests.get(f"{self.backend_url}/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "unknown")
                features = data.get("features", {})
                
                if status == "running":
                    self.log_result("Backend Status", True, "Backend running successfully")
                    
                    # Check individual features
                    feature_tests = [
                        ("sklearn_available", "Machine Learning"),
                        ("tmdb_available", "TMDB API"),
                        ("database_available", "Database"),
                        ("firebase_available", "Firebase")
                    ]
                    
                    for feature_key, feature_name in feature_tests:
                        if features.get(feature_key, False):
                            self.log_result(f"Feature {feature_name}", True, f"{feature_name} available")
                        else:
                            self.log_result(f"Feature {feature_name}", False, f"{feature_name} not available")
                            
                else:
                    self.log_result("Backend Status", False, f"Status: {status}")
                    
            else:
                self.log_result("Backend Status", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("Backend Status", False, f"Status check failed: {str(e)}")
            
    def test_movie_search(self):
        """Test movie search functionality"""
        print("\n🔍 Testing Movie Search...")
        
        test_queries = ["action", "comedy", "drama", "avengers"]
        
        for query in test_queries:
            try:
                response = requests.get(f"{self.backend_url}/movies/search?q={query}", timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    movies = data.get("movies", [])
                    
                    if movies and len(movies) > 0:
                        self.log_result(f"Movie Search '{query}'", True, f"Found {len(movies)} movies")
                        
                        # Check movie structure
                        first_movie = movies[0]
                        required_fields = ["id", "title", "overview", "poster_path"]
                        missing_fields = [field for field in required_fields if field not in first_movie]
                        
                        if not missing_fields:
                            self.log_result(f"Movie Data Structure '{query}'", True, "Movie data structure complete")
                        else:
                            self.log_result(f"Movie Data Structure '{query}'", False, f"Missing fields: {missing_fields}")
                            
                    else:
                        self.log_result(f"Movie Search '{query}'", False, "No movies found")
                        
                else:
                    self.log_result(f"Movie Search '{query}'", False, f"Status code: {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Movie Search '{query}'", False, f"Search failed: {str(e)}")
                
    def test_random_movies(self):
        """Test random movie endpoint"""
        print("\n🔍 Testing Random Movies...")
        
        try:
            response = requests.get(f"{self.backend_url}/movies/random", timeout=15)
            if response.status_code == 200:
                data = response.json()
                movies = data.get("movies", [])
                
                if movies and len(movies) > 0:
                    self.log_result("Random Movies", True, f"Retrieved {len(movies)} random movies")
                else:
                    self.log_result("Random Movies", False, "No random movies returned")
                    
            else:
                self.log_result("Random Movies", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("Random Movies", False, f"Random movies failed: {str(e)}")
            
    def test_movie_rating(self):
        """Test movie rating functionality"""
        print("\n🔍 Testing Movie Rating...")
        
        # Test rating submission
        test_rating = {
            "user_id": "test_user_123",
            "rating": 4.5
        }
        
        try:
            response = requests.post(
                f"{self.backend_url}/movies/550/rate",  # Fight Club movie ID
                json=test_rating,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success", False):
                    self.log_result("Movie Rating", True, "Rating submitted successfully")
                else:
                    self.log_result("Movie Rating", False, f"Rating failed: {data.get('message', 'Unknown error')}")
            else:
                self.log_result("Movie Rating", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("Movie Rating", False, f"Rating submission failed: {str(e)}")
            
    def test_recommendations(self):
        """Test recommendation system"""
        print("\n🔍 Testing Recommendations...")
        
        try:
            response = requests.get(f"{self.backend_url}/recommendations/1", timeout=20)
            if response.status_code == 200:
                data = response.json()
                recommendations = data.get("recommendations", [])
                
                if recommendations:
                    self.log_result("Recommendations", True, f"Generated {len(recommendations)} recommendations")
                else:
                    # This might be expected if no data exists yet
                    self.log_result("Recommendations", True, "No recommendations (expected for new system)")
                    
            else:
                self.log_result("Recommendations", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("Recommendations", False, f"Recommendations failed: {str(e)}")
            
    def test_frontend_availability(self):
        """Test frontend availability"""
        print("\n🔍 Testing Frontend Availability...")
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                if "AI Movie Recommendation Engine" in response.text or "React" in response.text:
                    self.log_result("Frontend Availability", True, "Frontend is accessible")
                else:
                    self.log_result("Frontend Availability", False, "Frontend content unexpected")
            else:
                self.log_result("Frontend Availability", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("Frontend Availability", False, f"Frontend not accessible: {str(e)}")
            
    def test_cors_headers(self):
        """Test CORS headers for frontend-backend communication"""
        print("\n🔍 Testing CORS Configuration...")
        
        try:
            headers = {
                'Origin': self.frontend_url,
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = requests.options(f"{self.backend_url}/movies/search", headers=headers, timeout=10)
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            if cors_headers['Access-Control-Allow-Origin']:
                self.log_result("CORS Configuration", True, "CORS headers present")
            else:
                self.log_result("CORS Configuration", False, "Missing CORS headers")
                
        except Exception as e:
            self.log_result("CORS Configuration", False, f"CORS test failed: {str(e)}")
            
    def run_all_tests(self):
        """Run all system tests"""
        print("🚀 Starting Full System Test")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        self.test_backend_health()
        self.test_backend_status()
        self.test_movie_search()
        self.test_random_movies()
        self.test_movie_rating()
        self.test_recommendations()
        self.test_frontend_availability()
        self.test_cors_headers()
        
        end_time = time.time()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if "✅ PASS" in result["status"])
        failed = sum(1 for result in self.test_results if "❌ FAIL" in result["status"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print(f"Test Duration: {end_time - start_time:.2f} seconds")
        
        if failed > 0:
            print("\n🔧 FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['message']}")
        else:
            print("\n🎉 ALL TESTS PASSED!")
            
        return passed == total

if __name__ == "__main__":
    tester = FullSystemTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ SYSTEM IS FULLY OPERATIONAL!")
    else:
        print("\n⚠️  SYSTEM HAS ISSUES - CHECK FAILED TESTS ABOVE")
