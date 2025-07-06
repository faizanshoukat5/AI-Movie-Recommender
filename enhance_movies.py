"""
Script to batch enhance movies with TMDB data (posters, metadata)
Run this to pre-populate movie posters and metadata for better user experience
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tmdb_client import TMDBClient
from rating_db import RatingDatabase
import pandas as pd
import time
import random

def load_movie_titles():
    """Load movie titles from u.item file"""
    movie_titles = {}
    movies_file = 'ml-100k/u.item'
    
    if os.path.exists(movies_file):
        try:
            with open(movies_file, 'r', encoding='iso-8859-1') as f:
                for line in f:
                    fields = line.strip().split('|')
                    if len(fields) >= 2:
                        movie_id = int(fields[0])
                        title = fields[1]
                        movie_titles[movie_id] = title
        except Exception as e:
            print(f"Error loading movie titles: {e}")
    
    return movie_titles

def extract_year(title):
    """Extract year from movie title"""
    import re
    match = re.search(r'\((\d{4})\)', title)
    return int(match.group(1)) if match else None

def enhance_movies_batch(limit=100, start_from=1):
    """
    Enhance movies with TMDB data
    
    Args:
        limit: Number of movies to enhance
        start_from: Movie ID to start from
    """
    print("🎬 Starting movie enhancement with TMDB data...")
    
    # Initialize clients
    tmdb_client = TMDBClient()
    rating_db = RatingDatabase()
    
    # Load movie titles
    movie_titles = load_movie_titles()
    print(f"📚 Loaded {len(movie_titles)} movies from dataset")
    
    # Get movies to enhance
    movie_ids = sorted([mid for mid in movie_titles.keys() if mid >= start_from])[:limit]
    
    enhanced_count = 0
    cached_count = 0
    error_count = 0
    
    print(f"🚀 Enhancing {len(movie_ids)} movies starting from ID {start_from}...")
    
    for i, movie_id in enumerate(movie_ids):
        try:
            # Check if already cached
            cached_metadata = rating_db.get_movie_metadata(movie_id)
            if cached_metadata:
                cached_count += 1
                print(f"✅ [{i+1}/{len(movie_ids)}] Movie {movie_id} already cached: {movie_titles[movie_id]}")
                continue
            
            title = movie_titles[movie_id]
            year = extract_year(title)
            
            print(f"🔍 [{i+1}/{len(movie_ids)}] Searching for: {title} ({year})")
            
            # Search for movie on TMDB
            tmdb_data = tmdb_client.search_movie(title, year)
            
            if tmdb_data:
                # Get detailed information
                detailed_data = tmdb_client.get_movie_details(tmdb_data['id'])
                
                if detailed_data:
                    # Cache the metadata
                    success = rating_db.cache_movie_metadata(movie_id, detailed_data)
                    
                    if success:
                        enhanced_count += 1
                        poster_url = tmdb_client.get_poster_url(detailed_data.get('poster_path'))
                        print(f"✅ [{i+1}/{len(movie_ids)}] Enhanced: {title}")
                        print(f"   TMDB ID: {detailed_data.get('id')}, Poster: {'Yes' if poster_url else 'No'}")
                    else:
                        error_count += 1
                        print(f"❌ [{i+1}/{len(movie_ids)}] Failed to cache: {title}")
                else:
                    error_count += 1
                    print(f"❌ [{i+1}/{len(movie_ids)}] No detailed data: {title}")
            else:
                error_count += 1
                print(f"❌ [{i+1}/{len(movie_ids)}] Not found on TMDB: {title}")
            
            # Add delay to respect TMDB rate limits (40 requests per 10 seconds)
            time.sleep(0.25)  # 4 requests per second
            
        except Exception as e:
            error_count += 1
            print(f"❌ [{i+1}/{len(movie_ids)}] Error processing {movie_id}: {e}")
    
    print(f"\n📊 Enhancement Summary:")
    print(f"✅ Enhanced: {enhanced_count}")
    print(f"💾 Already Cached: {cached_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📈 Total Processed: {len(movie_ids)}")
    print(f"🎯 Success Rate: {((enhanced_count + cached_count) / len(movie_ids) * 100):.1f}%")

def enhance_popular_movies():
    """Enhance most popular movies first (those with most ratings)"""
    print("🔥 Enhancing popular movies first...")
    
    # Load ratings data to find popular movies
    try:
        data = pd.read_csv('ml-100k/u.data', sep='\t', names=['user_id', 'item_id', 'rating', 'timestamp'])
        
        # Count ratings per movie
        movie_popularity = data['item_id'].value_counts()
        popular_movie_ids = movie_popularity.head(50).index.tolist()
        
        print(f"📈 Found {len(popular_movie_ids)} popular movies")
        
        # Load movie titles
        movie_titles = load_movie_titles()
        
        # Initialize clients
        tmdb_client = TMDBClient()
        rating_db = RatingDatabase()
        
        enhanced_count = 0
        
        for i, movie_id in enumerate(popular_movie_ids):
            try:
                # Check if already cached
                cached_metadata = rating_db.get_movie_metadata(movie_id)
                if cached_metadata:
                    continue
                
                title = movie_titles.get(movie_id, f"Movie {movie_id}")
                year = extract_year(title)
                rating_count = movie_popularity[movie_id]
                
                print(f"🔍 [{i+1}/{len(popular_movie_ids)}] {title} ({rating_count} ratings)")
                
                # Search and enhance
                tmdb_data = tmdb_client.search_movie(title, year)
                if tmdb_data:
                    detailed_data = tmdb_client.get_movie_details(tmdb_data['id'])
                    if detailed_data:
                        rating_db.cache_movie_metadata(movie_id, detailed_data)
                        enhanced_count += 1
                        print(f"✅ Enhanced: {title}")
                
                time.sleep(0.25)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error enhancing {movie_id}: {e}")
        
        print(f"\n🎉 Enhanced {enhanced_count} popular movies!")
        
    except Exception as e:
        print(f"Error loading popularity data: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhance movies with TMDB data')
    parser.add_argument('--popular', action='store_true', help='Enhance popular movies first')
    parser.add_argument('--limit', type=int, default=100, help='Number of movies to enhance')
    parser.add_argument('--start', type=int, default=1, help='Movie ID to start from')
    
    args = parser.parse_args()
    
    if args.popular:
        enhance_popular_movies()
    else:
        enhance_movies_batch(limit=args.limit, start_from=args.start)
    
    print("\n🎬 Movie enhancement complete! Your recommendation engine now has movie posters! 🎉")
