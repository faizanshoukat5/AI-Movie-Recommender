import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Import page components
import Navigation from './components/Navigation';
import HomePage from './pages/HomePage';
import RecommendationsPage from './pages/RecommendationsPage';
import MyRatingsPage from './pages/MyRatingsPage';
import PredictRatingPage from './pages/PredictRatingPage';
import ModelComparisonPage from './pages/ModelComparisonPage';

// API Configuration - will use environment variable in production
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function App() {
  const [recommendations, setRecommendations] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [movies, setMovies] = useState([]);
  const [filteredMovies, setFilteredMovies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [error, setError] = useState('');
  const [modelComparison, setModelComparison] = useState(null);
  const [availableModels, setAvailableModels] = useState([]);

  // Form state
  const [userId, setUserId] = useState(1);
  const [itemId, setItemId] = useState(1);
  const [numRecommendations, setNumRecommendations] = useState(10);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('title');
  const [selectedModel, setSelectedModel] = useState('ensemble');

  // New state for ratings and enhanced features
  const [userRatings, setUserRatings] = useState({});
  const [watchlist, setWatchlist] = useState([]);
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [selectedMovieForRating, setSelectedMovieForRating] = useState(null);

  // Initialize data
  useEffect(() => {
    fetchMovies();
    fetchRandomMovies();
    fetchAvailableModels();
    fetchUserRatings();
  }, []);

  // Update user ratings when userId changes
  useEffect(() => {
    fetchUserRatings();
  }, [userId]);

  // Handle search
  useEffect(() => {
    if (searchQuery && searchQuery.length > 2) {
      searchMovies();
    } else if (searchQuery.length === 0) {
      setFilteredMovies(sortMovies(movies.slice(0, 100), sortBy));
    }
  }, [searchQuery, sortBy, movies]);

  // Fetch available models
  const fetchAvailableModels = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/models`);
      if (!response.ok) throw new Error('Failed to fetch models');
      const data = await response.json();
      setAvailableModels(data.available_models || []);
    } catch (err) {
      setError(`Error fetching models: ${err.message}`);
    }
  };

  // Search movies via API
  const searchMovies = async () => {
    setSearchLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(searchQuery)}&sort=${sortBy}&limit=50&include_posters=true`);
      if (!response.ok) throw new Error('Failed to search movies');
      const data = await response.json();
      setFilteredMovies(data.movies || []);
    } catch (err) {
      setError(`Error searching movies: ${err.message}`);
      setFilteredMovies([]);
    } finally {
      setSearchLoading(false);
    }
  };

  // Get random movies for initial display
  const fetchRandomMovies = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/movies/random?limit=50&include_posters=true`);
      if (!response.ok) throw new Error('Failed to fetch random movies');
      const data = await response.json();
      setFilteredMovies(data.movies || []);
    } catch (err) {
      setError(`Error fetching random movies: ${err.message}`);
      setFilteredMovies([]);
    } finally {
      setLoading(false);
    }
  };

  // Sort movies
  const sortMovies = (movieList, sortType) => {
    return [...movieList].sort((a, b) => {
      switch (sortType) {
        case 'title':
          return a.title.localeCompare(b.title);
        case 'id':
          return a.id - b.id;
        case 'year':
          const yearA = a.title.match(/\\((\\d{4})\\)/)?.[1] || '0';
          const yearB = b.title.match(/\\((\\d{4})\\)/)?.[1] || '0';
          return yearB - yearA;
        default:
          return 0;
      }
    });
  };

  // Fetch movies
  const fetchMovies = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/movies?include_posters=true`);
      if (!response.ok) throw new Error('Failed to fetch movies');
      const data = await response.json();
      setMovies(data.movies || []);
      setFilteredMovies(data.movies || []);
    } catch (err) {
      setError(`Error fetching movies: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Get recommendations
  const handleGetRecommendations = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/recommendations/${userId}?model=${selectedModel}&limit=${numRecommendations}`);
      if (!response.ok) throw new Error('Failed to get recommendations');
      const data = await response.json();
      setRecommendations(data.recommendations || []);
    } catch (err) {
      setError(`Error getting recommendations: ${err.message}`);
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  // Predict rating
  const handlePredictRating = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/predict?user_id=${userId}&item_id=${itemId}&model=${selectedModel}`);
      if (!response.ok) throw new Error('Failed to predict rating');
      const data = await response.json();
      setPrediction(data);
    } catch (err) {
      setError(`Error predicting rating: ${err.message}`);
      setPrediction(null);
    } finally {
      setLoading(false);
    }
  };

  // Compare models
  const handleCompareModels = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/compare/${userId}`);
      if (!response.ok) throw new Error('Failed to compare models');
      const data = await response.json();
      setModelComparison(data);
    } catch (err) {
      setError(`Error comparing models: ${err.message}`);
      setModelComparison(null);
    } finally {
      setLoading(false);
    }
  };

  // Fetch user ratings
  const fetchUserRatings = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/users/${userId}/ratings`);
      if (!response.ok) throw new Error('Failed to fetch user ratings');
      const data = await response.json();
      setUserRatings(data.ratings || {});
    } catch (err) {
      console.error('Error fetching user ratings:', err);
      setUserRatings({});
    }
  };

  // Rate movie
  const handleRateMovie = async (movieId, rating) => {
    try {
      const response = await fetch(`${API_BASE_URL}/movies/${movieId}/rate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          rating: rating,
          user_id: userId
        }),
      });

      if (!response.ok) throw new Error('Failed to rate movie');
      
      // Update local state
      setUserRatings(prev => ({
        ...prev,
        [movieId]: rating
      }));
      
      setShowRatingModal(false);
    } catch (err) {
      setError(`Error rating movie: ${err.message}`);
    }
  };

  // Extract year from title
  const extractYear = (title) => {
    const match = title.match(/\\((\\d{4})\\)/);
    return match ? parseInt(match[1]) : null;
  };

  // Rating Modal Component
  const RatingModal = ({ movie, currentRating, onClose, onRate }) => {
    const [selectedRating, setSelectedRating] = useState(currentRating);
    const [hoveredRating, setHoveredRating] = useState(0);

    return (
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
        <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 max-w-md w-full border border-white/20">
          <h3 className="text-xl font-bold text-white mb-4">Rate Movie</h3>
          
          <div className="mb-4">
            <h4 className="text-white font-semibold mb-2">{movie.title}</h4>
            {movie.poster_url && (
              <img 
                src={movie.poster_url} 
                alt={movie.title}
                className="w-20 h-30 object-cover rounded mx-auto"
              />
            )}
          </div>
          
          <div className="flex justify-center mb-6">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                className={`text-3xl transition-colors ${
                  star <= (hoveredRating || selectedRating) ? 'text-yellow-400' : 'text-gray-500'
                }`}
                onMouseEnter={() => setHoveredRating(star)}
                onMouseLeave={() => setHoveredRating(0)}
                onClick={() => setSelectedRating(star)}
              >
                ★
              </button>
            ))}
          </div>
          
          <div className="flex gap-3">
            <button
              onClick={() => onRate(movie.id, selectedRating)}
              disabled={selectedRating === 0}
              className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 text-white font-semibold py-2 px-4 rounded-lg transition-all duration-200"
            >
              Rate Movie
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    );
  };

  // Movie Card Component
  const MovieCard = ({ movie }) => {
    const userRating = userRatings[movie.id];

    return (
      <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 hover:bg-white/20 hover:border-white/40 hover:shadow-lg hover:shadow-purple-500/20 transition-all duration-300 group transform hover:-translate-y-1 overflow-hidden">
        {/* Movie Poster */}
        {movie.poster_url ? (
          <div className="aspect-[2/3] overflow-hidden">
            <img 
              src={movie.poster_url}
              alt={movie.title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              onError={(e) => {
                e.target.parentElement.innerHTML = `
                  <div class="w-full h-full bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center">
                    <span class="text-gray-400 text-4xl">🎬</span>
                  </div>
                `;
              }}
            />
          </div>
        ) : (
          <div className="aspect-[2/3] bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center">
            <span className="text-gray-400 text-4xl">🎬</span>
          </div>
        )}
        
        {/* Movie Info */}
        <div className="p-4">
          <div className="flex items-start justify-between mb-2">
            <h3 className="font-semibold text-white group-hover:text-purple-200 transition-colors line-clamp-2 flex-1">
              {movie.title}
            </h3>
            <span className="text-sm text-gray-300 bg-white/10 px-2 py-1 rounded ml-2 shrink-0">
              #{movie.id}
            </span>
          </div>
          
          {movie.year && movie.year > 0 && (
            <div className="text-sm text-gray-300 mb-2">
              📅 {movie.year}
            </div>
          )}
          
          {/* User Rating Display */}
          {userRating && (
            <div className="flex items-center gap-2 mb-2">
              <span className="text-sm text-gray-300">Your rating:</span>
              <div className="flex">
                {[1, 2, 3, 4, 5].map((star) => (
                  <span key={star} className={`${star <= userRating ? 'text-yellow-400' : 'text-gray-500'}`}>
                    ★
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {/* Average User Rating */}
          {movie.user_rating && (
            <div className="flex items-center gap-2 mb-3">
              <span className="text-sm text-gray-300">Rating:</span>
              <div className="flex items-center gap-1">
                <span className="text-yellow-400">★</span>
                <span className="text-white font-semibold">{movie.user_rating}</span>
                <span className="text-gray-400 text-sm">({movie.user_rating_count})</span>
              </div>
            </div>
          )}
          
          {/* Predicted Rating */}
          {movie.predicted_rating && (
            <div className="flex items-center gap-2 mb-3">
              <span className="text-sm text-gray-300">Predicted:</span>
              <div className="flex items-center gap-1">
                <span className="text-green-400">★</span>
                <span className="text-white font-semibold">{movie.predicted_rating.toFixed(2)}</span>
              </div>
            </div>
          )}
          
          {/* Genres */}
          {movie.genres && (
            <div className="text-xs text-gray-400 mb-3 line-clamp-2">
              {movie.genres}
            </div>
          )}
          
          {/* Action Buttons */}
          <div className="flex gap-2">
            <button
              onClick={() => {
                setSelectedMovieForRating(movie);
                setShowRatingModal(true);
              }}
              className="flex-1 bg-gradient-to-r from-purple-600/80 to-pink-600/80 hover:from-purple-600 hover:to-pink-600 text-white text-sm font-medium py-2 px-3 rounded-md transition-all duration-200 transform hover:scale-105"
            >
              {userRating ? 'Edit Rating' : 'Rate Movie'}
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
        <Navigation />
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route 
              path="/" 
              element={
                <HomePage 
                  filteredMovies={filteredMovies}
                  loading={loading}
                  searchLoading={searchLoading}
                  searchQuery={searchQuery}
                  setSearchQuery={setSearchQuery}
                  sortBy={sortBy}
                  setSortBy={setSortBy}
                  MovieCard={MovieCard}
                  error={error}
                />
              } 
            />
            <Route 
              path="/recommendations" 
              element={
                <RecommendationsPage 
                  recommendations={recommendations}
                  loading={loading}
                  userId={userId}
                  setUserId={setUserId}
                  numRecommendations={numRecommendations}
                  setNumRecommendations={setNumRecommendations}
                  selectedModel={selectedModel}
                  setSelectedModel={setSelectedModel}
                  availableModels={availableModels}
                  handleGetRecommendations={handleGetRecommendations}
                  MovieCard={MovieCard}
                  error={error}
                />
              } 
            />
            <Route 
              path="/ratings" 
              element={
                <MyRatingsPage 
                  userRatings={userRatings}
                  movies={movies}
                  userId={userId}
                  handleRateMovie={handleRateMovie}
                  showRatingModal={showRatingModal}
                  setShowRatingModal={setShowRatingModal}
                  selectedMovieForRating={selectedMovieForRating}
                  setSelectedMovieForRating={setSelectedMovieForRating}
                  RatingModal={RatingModal}
                />
              } 
            />
            <Route 
              path="/predict" 
              element={
                <PredictRatingPage 
                  prediction={prediction}
                  loading={loading}
                  userId={userId}
                  setUserId={setUserId}
                  itemId={itemId}
                  setItemId={setItemId}
                  selectedModel={selectedModel}
                  setSelectedModel={setSelectedModel}
                  availableModels={availableModels}
                  handlePredictRating={handlePredictRating}
                  movies={movies}
                  error={error}
                />
              } 
            />
            <Route 
              path="/compare" 
              element={
                <ModelComparisonPage 
                  modelComparison={modelComparison}
                  loading={loading}
                  userId={userId}
                  setUserId={setUserId}
                  handleCompareModels={handleCompareModels}
                  error={error}
                />
              } 
            />
          </Routes>
        </main>

        {/* Rating Modal */}
        {showRatingModal && selectedMovieForRating && (
          <RatingModal
            movie={selectedMovieForRating}
            currentRating={userRatings[selectedMovieForRating.id] || 0}
            onClose={() => setShowRatingModal(false)}
            onRate={handleRateMovie}
          />
        )}
      </div>
    </Router>
  );
}

export default App;
