// TMDB API Integration for Movie Posters and Details
const TMDB_API_KEY = process.env.REACT_APP_TMDB_API_KEY;
const TMDB_BASE_URL = 'https://api.themoviedb.org/3';
const TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500';

class TMDBService {
  constructor() {
    this.cache = new Map();
    this.cacheTimeout = 30 * 60 * 1000; // 30 minutes
  }

  // Get API key from environment or use demo key
  getApiKey() {
    return TMDB_API_KEY || 'demo_key_please_add_your_own';
  }

  // Search for movie by title
  async searchMovie(title, year = null) {
    try {
      const cacheKey = `search_${title}_${year}`;
      
      // Check cache first
      if (this.cache.has(cacheKey)) {
        const cached = this.cache.get(cacheKey);
        if (Date.now() - cached.timestamp < this.cacheTimeout) {
          return cached.data;
        }
      }

      const cleanTitle = title.replace(/\([^)]*\)/g, '').trim();
      let url = `${TMDB_BASE_URL}/search/movie?api_key=${this.getApiKey()}&query=${encodeURIComponent(cleanTitle)}`;
      
      if (year) {
        url += `&year=${year}`;
      }

      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`TMDB API error: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Cache the result
      this.cache.set(cacheKey, {
        data,
        timestamp: Date.now()
      });
      
      return data;
    } catch (error) {
      console.error('Error searching movie:', error);
      return { results: [] };
    }
  }

  // Get movie details by ID
  async getMovieDetails(tmdbId) {
    try {
      const cacheKey = `details_${tmdbId}`;
      
      if (this.cache.has(cacheKey)) {
        const cached = this.cache.get(cacheKey);
        if (Date.now() - cached.timestamp < this.cacheTimeout) {
          return cached.data;
        }
      }

      const response = await fetch(
        `${TMDB_BASE_URL}/movie/${tmdbId}?api_key=${this.getApiKey()}&append_to_response=credits,videos`
      );
      
      if (!response.ok) {
        throw new Error(`TMDB API error: ${response.status}`);
      }
      
      const data = await response.json();
      
      this.cache.set(cacheKey, {
        data,
        timestamp: Date.now()
      });
      
      return data;
    } catch (error) {
      console.error('Error fetching movie details:', error);
      return null;
    }
  }

  // Get poster URL
  getPosterUrl(posterPath, size = 'w500') {
    if (!posterPath) return null;
    return `https://image.tmdb.org/t/p/${size}${posterPath}`;
  }

  // Get backdrop URL
  getBackdropUrl(backdropPath, size = 'w1280') {
    if (!backdropPath) return null;
    return `https://image.tmdb.org/t/p/${size}${backdropPath}`;
  }

  // Extract year from movie title
  extractYear(title) {
    const yearMatch = title.match(/\((\d{4})\)/);
    return yearMatch ? parseInt(yearMatch[1]) : null;
  }

  // Find best matching movie from search results
  findBestMatch(searchResults, originalTitle, year = null) {
    if (!searchResults || !searchResults.results || searchResults.results.length === 0) {
      return null;
    }

    const results = searchResults.results;
    
    // If we have a year, prioritize exact year matches
    if (year) {
      const exactYearMatch = results.find(movie => {
        const releaseYear = movie.release_date ? new Date(movie.release_date).getFullYear() : null;
        return releaseYear === year;
      });
      
      if (exactYearMatch) {
        return exactYearMatch;
      }
    }

    // Otherwise, return the first result (most popular/relevant)
    return results[0];
  }

  // Enhanced movie search with better matching
  async enhanceMovieData(movie) {
    try {
      const { title, id } = movie;
      const year = this.extractYear(title);
      const cleanTitle = title.replace(/\([^)]*\)/g, '').trim();
      
      const searchResults = await this.searchMovie(cleanTitle, year);
      const bestMatch = this.findBestMatch(searchResults, title, year);
      
      if (bestMatch) {
        const movieDetails = await this.getMovieDetails(bestMatch.id);
        
        return {
          ...movie,
          tmdbId: bestMatch.id,
          poster: this.getPosterUrl(bestMatch.poster_path),
          backdrop: this.getBackdropUrl(bestMatch.backdrop_path),
          overview: bestMatch.overview,
          tmdbRating: bestMatch.vote_average,
          voteCount: bestMatch.vote_count,
          releaseDate: bestMatch.release_date,
          genres: movieDetails?.genres || [],
          cast: movieDetails?.credits?.cast?.slice(0, 5) || [],
          director: movieDetails?.credits?.crew?.find(person => person.job === 'Director')?.name || '',
          runtime: movieDetails?.runtime || 0,
          trailer: movieDetails?.videos?.results?.find(video => 
            video.type === 'Trailer' && video.site === 'YouTube'
          )?.key || null
        };
      }
      
      return {
        ...movie,
        poster: null,
        backdrop: null,
        overview: 'No description available.',
        tmdbRating: 0,
        voteCount: 0
      };
    } catch (error) {
      console.error('Error enhancing movie data:', error);
      return {
        ...movie,
        poster: null,
        backdrop: null,
        overview: 'No description available.',
        tmdbRating: 0,
        voteCount: 0
      };
    }
  }

  // Batch enhance multiple movies
  async enhanceMoviesBatch(movies, batchSize = 5) {
    const enhanced = [];
    
    for (let i = 0; i < movies.length; i += batchSize) {
      const batch = movies.slice(i, i + batchSize);
      
      const batchPromises = batch.map(movie => this.enhanceMovieData(movie));
      const batchResults = await Promise.all(batchPromises);
      
      enhanced.push(...batchResults);
      
      // Small delay to avoid rate limiting
      if (i + batchSize < movies.length) {
        await new Promise(resolve => setTimeout(resolve, 100));
      }
    }
    
    return enhanced;
  }

  // Get trending movies
  async getTrendingMovies(timeWindow = 'day') {
    try {
      const response = await fetch(
        `${TMDB_BASE_URL}/trending/movie/${timeWindow}?api_key=${this.getApiKey()}`
      );
      
      if (!response.ok) {
        throw new Error(`TMDB API error: ${response.status}`);
      }
      
      const data = await response.json();
      return data.results || [];
    } catch (error) {
      console.error('Error fetching trending movies:', error);
      return [];
    }
  }

  // Get movie recommendations from TMDB
  async getMovieRecommendations(tmdbId) {
    try {
      const response = await fetch(
        `${TMDB_BASE_URL}/movie/${tmdbId}/recommendations?api_key=${this.getApiKey()}`
      );
      
      if (!response.ok) {
        throw new Error(`TMDB API error: ${response.status}`);
      }
      
      const data = await response.json();
      return data.results || [];
    } catch (error) {
      console.error('Error fetching TMDB recommendations:', error);
      return [];
    }
  }

  // Clear cache
  clearCache() {
    this.cache.clear();
  }
}

// Export singleton instance
export const tmdbService = new TMDBService();
export default tmdbService;
