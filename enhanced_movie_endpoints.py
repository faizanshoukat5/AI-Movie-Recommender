"""
Enhanced movie search endpoint for PythonAnywhere
This replaces the existing search_movies function with improved metadata handling
"""

@app.route('/movies/search')
@simple_cache(timeout=300)
def search_movies():
    """Search movies with enhanced metadata"""
    query = request.args.get('q', '').lower()
    limit = request.args.get('limit', 50, type=int)
    include_posters = request.args.get('include_posters', 'true').lower() == 'true'
    
    if not query:
        return jsonify({'error': 'Query parameter q is required'}), 400
    
    # Filter movies
    matching_movies = []
    for movie_id, title in movie_titles.items():
        if query in title.lower():
            movie_info = {
                'id': movie_id,
                'title': title,
                'year': extract_year(title),
                'genres': movie_genres.get(movie_id, []),
                # Add required fields with defaults
                'overview': f"Classic movie from the MovieLens dataset: {title}",
                'poster_path': None,
                'backdrop_path': None,
                'release_date': None,
                'vote_average': 0.0,
                'vote_count': 0
            }
            
            # Try to get enhanced metadata
            if tmdb_client and rating_db:
                try:
                    # Check if we have cached metadata
                    cached_metadata = rating_db.get_movie_metadata(movie_id)
                    if cached_metadata:
                        movie_info.update({
                            'overview': cached_metadata.get('overview', movie_info['overview']),
                            'poster_path': cached_metadata.get('poster_path'),
                            'backdrop_path': cached_metadata.get('backdrop_path'),
                            'release_date': cached_metadata.get('release_date'),
                            'vote_average': cached_metadata.get('vote_average', 0.0),
                            'vote_count': cached_metadata.get('vote_count', 0)
                        })
                        
                        # Add poster URL if available
                        if include_posters and cached_metadata.get('poster_path'):
                            movie_info['poster_url'] = tmdb_client.get_poster_url(cached_metadata['poster_path'])
                    else:
                        # Try to fetch from TMDB
                        search_results = tmdb_client.search_movie(title)
                        if search_results and search_results.get('results'):
                            tmdb_movie = search_results['results'][0]
                            
                            # Update movie info with TMDB data
                            movie_info.update({
                                'overview': tmdb_movie.get('overview', movie_info['overview']),
                                'poster_path': tmdb_movie.get('poster_path'),
                                'backdrop_path': tmdb_movie.get('backdrop_path'),
                                'release_date': tmdb_movie.get('release_date'),
                                'vote_average': tmdb_movie.get('vote_average', 0.0),
                                'vote_count': tmdb_movie.get('vote_count', 0)
                            })
                            
                            # Cache the metadata
                            rating_db.cache_movie_metadata(movie_id, tmdb_movie)
                            
                            # Add poster URL if available
                            if include_posters and tmdb_movie.get('poster_path'):
                                movie_info['poster_url'] = tmdb_client.get_poster_url(tmdb_movie['poster_path'])
                                
                except Exception as e:
                    logger.error(f"Error fetching movie metadata for {movie_id}: {e}")
                    # Keep default values
                    pass
            
            # Add ratings if available
            if rating_db:
                try:
                    avg_rating, rating_count = rating_db.get_average_rating(movie_id)
                    if avg_rating > 0:
                        movie_info['user_rating'] = round(avg_rating, 2)
                        movie_info['user_rating_count'] = rating_count
                except Exception as e:
                    logger.error(f"Error fetching ratings for {movie_id}: {e}")
                    pass
            
            matching_movies.append(movie_info)
    
    # Sort and limit
    matching_movies.sort(key=lambda x: x['title'])
    matching_movies = matching_movies[:limit]
    
    return jsonify({
        'movies': matching_movies,
        'total': len(matching_movies),
        'query': query
    })

@app.route('/movies/random')
@simple_cache(timeout=60)
def get_random_movies():
    """Get random movies with enhanced metadata"""
    limit = request.args.get('limit', 20, type=int)
    include_posters = request.args.get('include_posters', 'true').lower() == 'true'
    
    import random
    
    # Get random movies
    all_movies = list(movie_titles.items())
    if len(all_movies) > limit:
        selected_movies = random.sample(all_movies, limit)
    else:
        selected_movies = all_movies
    
    random_movies = []
    for movie_id, title in selected_movies:
        movie_info = {
            'id': movie_id,
            'title': title,
            'year': extract_year(title),
            'genres': movie_genres.get(movie_id, []),
            # Add required fields with defaults
            'overview': f"Classic movie from the MovieLens dataset: {title}",
            'poster_path': None,
            'backdrop_path': None,
            'release_date': None,
            'vote_average': 0.0,
            'vote_count': 0
        }
        
        # Try to get enhanced metadata (similar to search)
        if tmdb_client and rating_db:
            try:
                cached_metadata = rating_db.get_movie_metadata(movie_id)
                if cached_metadata:
                    movie_info.update({
                        'overview': cached_metadata.get('overview', movie_info['overview']),
                        'poster_path': cached_metadata.get('poster_path'),
                        'backdrop_path': cached_metadata.get('backdrop_path'),
                        'release_date': cached_metadata.get('release_date'),
                        'vote_average': cached_metadata.get('vote_average', 0.0),
                        'vote_count': cached_metadata.get('vote_count', 0)
                    })
                    
                    if include_posters and cached_metadata.get('poster_path'):
                        movie_info['poster_url'] = tmdb_client.get_poster_url(cached_metadata['poster_path'])
            except Exception as e:
                logger.error(f"Error fetching metadata for random movie {movie_id}: {e}")
                pass
        
        # Add ratings if available
        if rating_db:
            try:
                avg_rating, rating_count = rating_db.get_average_rating(movie_id)
                if avg_rating > 0:
                    movie_info['user_rating'] = round(avg_rating, 2)
                    movie_info['user_rating_count'] = rating_count
            except Exception as e:
                logger.error(f"Error fetching ratings for random movie {movie_id}: {e}")
                pass
        
        random_movies.append(movie_info)
    
    return jsonify({
        'movies': random_movies,
        'total': len(random_movies)
    })
