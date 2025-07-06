"""
TMDB API Client for Movie Poster and Metadata Integration
"""
import requests
import json
from typing import Optional, Dict, List
import os
from urllib.parse import quote

class TMDBClient:
    def __init__(self, api_key: str = None):
        """
        Initialize TMDB client with API key
        Get your API key from: https://www.themoviedb.org/settings/api
        """
        # Use provided API key, environment variable, or default
        self.api_key = api_key or os.getenv('TMDB_API_KEY') or '89cf1a0e526c7c36bafe8d77248d276d'
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p"
        self.session = requests.Session()
        
        if not self.api_key:
            print("Warning: TMDB API key not found. Movie posters will not be available.")
        else:
            print(f"TMDB client initialized with API key: {self.api_key[:8]}...")
    
    def search_movie(self, title: str, year: int = None) -> Optional[Dict]:
        """
        Search for a movie by title and optional year
        Returns the best match or None
        """
        if not self.api_key:
            return None
            
        try:
            # Clean the title for search
            clean_title = self._clean_title(title)
            
            params = {
                'api_key': self.api_key,
                'query': clean_title,
                'include_adult': False
            }
            
            if year:
                params['year'] = year
            
            response = self.session.get(f"{self.base_url}/search/movie", params=params)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            if not results:
                return None
            
            # Find the best match
            best_match = self._find_best_match(results, clean_title, year)
            return best_match
            
        except Exception as e:
            print(f"Error searching for movie '{title}': {e}")
            return None
    
    def get_movie_details(self, tmdb_id: int) -> Optional[Dict]:
        """
        Get detailed information about a movie
        """
        if not self.api_key:
            return None
            
        try:
            params = {
                'api_key': self.api_key,
                'append_to_response': 'credits,videos,similar'
            }
            
            response = self.session.get(f"{self.base_url}/movie/{tmdb_id}", params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error getting movie details for ID {tmdb_id}: {e}")
            return None
    
    def get_poster_url(self, poster_path: str, size: str = "w500") -> str:
        """
        Get full URL for movie poster
        Available sizes: w92, w154, w185, w342, w500, w780, original
        """
        if not poster_path:
            return None
        return f"{self.image_base_url}/{size}{poster_path}"
    
    def get_backdrop_url(self, backdrop_path: str, size: str = "w1280") -> str:
        """
        Get full URL for movie backdrop
        Available sizes: w300, w780, w1280, original
        """
        if not backdrop_path:
            return None
        return f"{self.image_base_url}/{size}{backdrop_path}"
    
    def _clean_title(self, title: str) -> str:
        """
        Clean movie title for better search results
        """
        # Remove year from title if present
        import re
        clean_title = re.sub(r'\s*\(\d{4}\)\s*', '', title)
        clean_title = clean_title.strip()
        return clean_title
    
    def _find_best_match(self, results: List[Dict], title: str, year: int = None) -> Optional[Dict]:
        """
        Find the best matching movie from search results
        """
        if not results:
            return None
        
        # If we have a year, try to find exact match
        if year:
            for movie in results:
                release_date = movie.get('release_date', '')
                if release_date and release_date.startswith(str(year)):
                    return movie
        
        # Otherwise, return the first result (most popular)
        return results[0]
    
    def batch_search_movies(self, movies: List[Dict]) -> Dict[int, Dict]:
        """
        Search for multiple movies and return a mapping of movie_id to TMDB data
        """
        results = {}
        
        for movie in movies:
            movie_id = movie.get('id')
            title = movie.get('title', '')
            
            # Extract year from title if present
            year = None
            import re
            year_match = re.search(r'\((\d{4})\)', title)
            if year_match:
                year = int(year_match.group(1))
            
            # Search for movie
            tmdb_data = self.search_movie(title, year)
            if tmdb_data:
                results[movie_id] = tmdb_data
        
        return results

# Example usage and testing
if __name__ == "__main__":
    # Test the TMDB client
    client = TMDBClient()
    
    # Test search
    movie = client.search_movie("Toy Story", 1995)
    if movie:
        print(f"Found: {movie['title']} ({movie['release_date']})")
        print(f"Poster: {client.get_poster_url(movie['poster_path'])}")
    else:
        print("Movie not found or API key not configured")
