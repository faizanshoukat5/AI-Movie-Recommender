import React, { useState, useEffect } from 'react';
iimport { AuthProvider, useAuth } from './AuthContext';
import AuthModal from './AuthModal';
import './App.css';

const API_BASE_URL = 'http://localhost:5000';

function AppContent() {
  const { currentUser, logout, getIdToken } = useAuth();
  
  // App state
  const [recommendations, setRecommendations] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [movies, setMovies] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [watchlist, setWatchlist] = useState([]);
  const [userRatings, setUserRatings] = useState({});
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('recommendations');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('login');

  // Movie rating state
  const [selectedMovieId, setSelectedMovieId] = useState('');
  const [ratingValue, setRatingValue] = useState(5);

  // Initialize data
  useEffect(() => {
    fetchRandomMovies();
    if (currentUser) {
      fetchUserData();
    }
  }, [currentUser]);

  // Fetch user-specific data
  const fetchUserData = async () => {
    try {
      await Promise.all([
        fetchRecommendations(),
        fetchWatchlist(),
        fetchUserRatings(),
        fetchAnalytics()
      ]);
    } catch (error) {
      console.error('Error fetching user data:', error);
    }
  };

  // API call helper with authentication
  const apiCall = async (endpoint, options = {}) => {
    const token = await getIdToken();
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Network error' }));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  };

  // Fetch recommendations
  const fetchRecommendations = async () => {
    if (!currentUser) return;

    setLoading(true);
    setError('');
    
    try {
      const data = await apiCall('/recommendations');
      setRecommendations(data.recommendations || []);
    } catch (err) {
      setError(`Error fetching recommendations: ${err.message}`);
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  // Fetch random movies
  const fetchRandomMovies = async () => {
    setLoading(true);
    try {
      const data = await apiCall('/movies/random');
      setMovies(data.movies || []);
    } catch (err) {
      console.error('Error fetching random movies:', err);
      setError('Failed to fetch movies');
    } finally {
      setLoading(false);
    }
  };

  // Search movies
  const searchMovies = async (query) => {
    if (!query.trim()) {
      fetchRandomMovies();
      return;
    }

    setLoading(true);
    try {
      const data = await apiCall(`/movies/search?q=${encodeURIComponent(query)}`);
      setMovies(data.movies || []);
    } catch (err) {
      console.error('Error searching movies:', err);
      setError('Failed to search movies');
    } finally {
      setLoading(false);
    }
  };

  // Fetch watchlist
  const fetchWatchlist = async () => {
    if (!currentUser) return;

    try {
      const data = await apiCall('/watchlist');
      setWatchlist(data.watchlist || []);
    } catch (err) {
      console.error('Error fetching watchlist:', err);
    }
  };

  // Add to watchlist
  const addToWatchlist = async (movieId) => {
    if (!currentUser) {
      setShowAuthModal(true);
      return;
    }

    try {
      await apiCall('/watchlist', {
        method: 'POST',
        body: JSON.stringify({ movie_id: movieId })
      });
      fetchWatchlist();
    } catch (err) {
      setError(`Error adding to watchlist: ${err.message}`);
    }
  };

  // Remove from watchlist
  const removeFromWatchlist = async (movieId) => {
    if (!currentUser) return;

    try {
      await apiCall(`/watchlist/${movieId}`, {
        method: 'DELETE'
      });
      fetchWatchlist();
    } catch (err) {
      setError(`Error removing from watchlist: ${err.message}`);
    }
  };

  // Fetch user ratings
  const fetchUserRatings = async () => {
    if (!currentUser) return;

    try {
      const data = await apiCall('/ratings');
      const ratingsMap = {};
      data.ratings.forEach(rating => {
        ratingsMap[rating.movie_id] = rating.rating;
      });
      setUserRatings(ratingsMap);
    } catch (err) {
      console.error('Error fetching user ratings:', err);
    }
  };

  // Rate movie
  const rateMovie = async (movieId, rating) => {
    if (!currentUser) {
      setShowAuthModal(true);
      return;
    }

    try {
      await apiCall('/ratings', {
        method: 'POST',
        body: JSON.stringify({ movie_id: movieId, rating: rating })
      });
      fetchUserRatings();
      if (activeTab === 'recommendations') {
        fetchRecommendations();
      }
    } catch (err) {
      setError(`Error rating movie: ${err.message}`);
    }
  };

  // Fetch analytics
  const fetchAnalytics = async () => {
    if (!currentUser) return;

    try {
      const data = await apiCall('/analytics');
      setAnalytics(data);
    } catch (err) {
      console.error('Error fetching analytics:', err);
    }
  };

  // Event handlers
  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  const handleSearchSubmit = () => {
    searchMovies(searchQuery);
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    fetchRandomMovies();
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearchSubmit();
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      setRecommendations([]);
      setWatchlist([]);
      setUserRatings({});
      setAnalytics(null);
      setActiveTab('movies');
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  const openAuthModal = (mode) => {
    setAuthMode(mode);
    setShowAuthModal(true);
  };

  const isInWatchlist = (movieId) => {
    return watchlist.some(item => item.movie_id === movieId);
  };

  // Components
  const TabButton = ({ id, label, isActive, onClick, disabled = false }) => (
    <button
      className={`tab-button ${isActive ? 'active' : ''} ${disabled ? 'disabled' : ''}`}
      onClick={() => onClick(id)}
      disabled={disabled}
    >
      {label}
    </button>
  );

  const MovieCard = ({ movie, showActions = true }) => (
    <div className="movie-card">
      <div className="movie-header">
        <h4>{movie.title}</h4>
        <div className="movie-meta">
          <span className="movie-id">ID: {movie.movie_id}</span>
          {movie.genres && <span className="movie-genres">{movie.genres.join(', ')}</span>}
        </div>
      </div>
      
      {showActions && (
        <div className="movie-actions">
          <div className="rating-section">
            <select 
              value={ratingValue} 
              onChange={(e) => setRatingValue(parseInt(e.target.value))}
              className="rating-select"
            >
              {[1, 2, 3, 4, 5].map(rating => (
                <option key={rating} value={rating}>{rating} ⭐</option>
              ))}
            </select>
            <button 
              onClick={() => rateMovie(movie.movie_id, ratingValue)}
              className="rate-button"
              disabled={!currentUser}
            >
              Rate
            </button>
          </div>
          
          <button
            onClick={() => isInWatchlist(movie.movie_id) 
              ? removeFromWatchlist(movie.movie_id) 
              : addToWatchlist(movie.movie_id)}
            className={`watchlist-button ${isInWatchlist(movie.movie_id) ? 'remove' : 'add'}`}
            disabled={!currentUser}
          >
            {isInWatchlist(movie.movie_id) ? '− Remove' : '+ Watchlist'}
          </button>
          
          {userRatings[movie.movie_id] && (
            <div className="user-rating">
              Your rating: {userRatings[movie.movie_id]}⭐
            </div>
          )}
        </div>
      )}
    </div>
  );

  const RecommendationCard = ({ item }) => (
    <div className="recommendation-card">
      <div className="recommendation-header">
        <h3>{item.title}</h3>
        <span className="rating-badge">{item.predicted_rating?.toFixed(2) || 'N/A'}</span>
      </div>
      <div className="recommendation-details">
        <p className="movie-id">ID: {item.movie_id}</p>
        <p className="rating-text">
          Predicted Rating: <strong>{item.predicted_rating?.toFixed(2) || 'N/A'}</strong>
        </p>
        {item.genres && (
          <p className="genres">Genres: {item.genres.join(', ')}</p>
        )}
      </div>
      <div className="recommendation-actions">
        <button
          onClick={() => isInWatchlist(item.movie_id) 
            ? removeFromWatchlist(item.movie_id) 
            : addToWatchlist(item.movie_id)}
          className={`watchlist-button ${isInWatchlist(item.movie_id) ? 'remove' : 'add'}`}
        >
          {isInWatchlist(item.movie_id) ? '− Remove' : '+ Watchlist'}
        </button>
      </div>
    </div>
  );

  return (
    <div className="App">
      <header className="app-header">
        <h1>🎬 AI Movie Recommendation Engine</h1>
        <p>Discover personalized movie recommendations powered by Firebase & AI</p>
        
        <div className="user-section">
          {currentUser ? (
            <div className="user-info">
              <span className="user-greeting">
                Welcome, {currentUser.displayName || currentUser.email}!
              </span>
              <button onClick={handleLogout} className="logout-button">
                Logout
              </button>
            </div>
          ) : (
            <div className="auth-buttons">
              <button onClick={() => openAuthModal('login')} className="auth-button">
                Sign In
              </button>
              <button onClick={() => openAuthModal('signup')} className="auth-button signup">
                Sign Up
              </button>
            </div>
          )}
        </div>
      </header>

      <div className="main-container">
        <nav className="tab-navigation">
          <TabButton
            id="movies"
            label="Browse Movies"
            isActive={activeTab === 'movies'}
            onClick={setActiveTab}
          />
          <TabButton
            id="recommendations"
            label="Recommendations"
            isActive={activeTab === 'recommendations'}
            onClick={setActiveTab}
            disabled={!currentUser}
          />
          <TabButton
            id="watchlist"
            label="My Watchlist"
            isActive={activeTab === 'watchlist'}
            onClick={setActiveTab}
            disabled={!currentUser}
          />
          <TabButton
            id="analytics"
            label="Analytics"
            isActive={activeTab === 'analytics'}
            onClick={setActiveTab}
            disabled={!currentUser}
          />
        </nav>

        <div className="content-container">
          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              {error}
              <button onClick={() => setError('')} className="error-close">×</button>
            </div>
          )}

          {!currentUser && (activeTab === 'recommendations' || activeTab === 'watchlist' || activeTab === 'analytics') && (
            <div className="auth-required">
              <h3>Authentication Required</h3>
              <p>Please sign in to access this feature.</p>
              <button onClick={() => openAuthModal('login')} className="auth-button">
                Sign In
              </button>
            </div>
          )}

          {activeTab === 'movies' && (
            <div className="tab-content">
              <div className="input-section">
                <h2>Browse Movies</h2>
                <div className="input-group">
                  <label htmlFor="movieSearch">Search Movies:</label>
                  <div className="search-container">
                    <input
                      id="movieSearch"
                      type="text"
                      value={searchQuery}
                      onChange={handleSearchChange}
                      onKeyPress={handleKeyPress}
                      placeholder="Search for movies by title..."
                    />
                    <div className="search-buttons">
                      <button 
                        className="search-button"
                        onClick={handleSearchSubmit}
                        disabled={loading}
                      >
                        🔍 Search
                      </button>
                      <button 
                        className="clear-button"
                        onClick={handleClearSearch}
                        disabled={loading}
                      >
                        🎲 Random
                      </button>
                    </div>
                  </div>
                </div>
                <p className="search-hint">
                  {searchQuery ? `Showing results for "${searchQuery}"` : 'Showing random movies'}
                </p>
              </div>

              {loading && (
                <div className="loading-section">
                  <div className="spinner"></div>
                  <p>Loading movies...</p>
                </div>
              )}

              {movies.length > 0 && !loading && (
                <div className="results-section">
                  <h3>Movies ({movies.length})</h3>
                  <div className="movies-grid">
                    {movies.map((movie, index) => (
                      <MovieCard key={index} movie={movie} />
                    ))}
                  </div>
                </div>
              )}

              {movies.length === 0 && !loading && (
                <div className="no-results">
                  <p>No movies found. Try a different search term or click "Random" to discover movies.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'recommendations' && currentUser && (
            <div className="tab-content">
              <div className="input-section">
                <h2>Personalized Recommendations</h2>
                <p>Based on your ratings and preferences</p>
                <button
                  className="primary-button"
                  onClick={fetchRecommendations}
                  disabled={loading}
                >
                  {loading ? 'Loading...' : 'Get Fresh Recommendations'}
                </button>
              </div>

              {loading && (
                <div className="loading-section">
                  <div className="spinner"></div>
                  <p>Generating recommendations...</p>
                </div>
              )}

              {recommendations.length > 0 && !loading && (
                <div className="results-section">
                  <h3>Your Recommendations</h3>
                  <div className="recommendations-grid">
                    {recommendations.map((item, index) => (
                      <RecommendationCard key={index} item={item} />
                    ))}
                  </div>
                </div>
              )}

              {recommendations.length === 0 && !loading && (
                <div className="no-results">
                  <p>No recommendations available. Try rating some movies first!</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'watchlist' && currentUser && (
            <div className="tab-content">
              <div className="input-section">
                <h2>My Watchlist</h2>
                <p>Movies you want to watch</p>
                <button
                  className="primary-button"
                  onClick={fetchWatchlist}
                  disabled={loading}
                >
                  {loading ? 'Loading...' : 'Refresh Watchlist'}
                </button>
              </div>

              {loading && (
                <div className="loading-section">
                  <div className="spinner"></div>
                  <p>Loading watchlist...</p>
                </div>
              )}

              {watchlist.length > 0 && !loading && (
                <div className="results-section">
                  <h3>Your Watchlist ({watchlist.length})</h3>
                  <div className="movies-grid">
                    {watchlist.map((movie, index) => (
                      <MovieCard key={index} movie={movie} showActions={false} />
                    ))}
                  </div>
                </div>
              )}

              {watchlist.length === 0 && !loading && (
                <div className="no-results">
                  <p>Your watchlist is empty. Add some movies from the Browse Movies tab!</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'analytics' && currentUser && (
            <div className="tab-content">
              <div className="input-section">
                <h2>Your Analytics</h2>
                <p>Insights about your movie preferences</p>
                <button
                  className="primary-button"
                  onClick={fetchAnalytics}
                  disabled={loading}
                >
                  {loading ? 'Loading...' : 'Refresh Analytics'}
                </button>
              </div>

              {loading && (
                <div className="loading-section">
                  <div className="spinner"></div>
                  <p>Loading analytics...</p>
                </div>
              )}

              {analytics && !loading && (
                <div className="results-section">
                  <div className="analytics-grid">
                    <div className="analytics-card">
                      <h3>Total Ratings</h3>
                      <div className="analytics-value">{analytics.total_ratings || 0}</div>
                    </div>
                    <div className="analytics-card">
                      <h3>Average Rating</h3>
                      <div className="analytics-value">
                        {analytics.average_rating ? analytics.average_rating.toFixed(1) : 'N/A'}⭐
                      </div>
                    </div>
                    <div className="analytics-card">
                      <h3>Watchlist Size</h3>
                      <div className="analytics-value">{analytics.watchlist_size || 0}</div>
                    </div>
                    <div className="analytics-card">
                      <h3>Favorite Genre</h3>
                      <div className="analytics-value">{analytics.favorite_genre || 'N/A'}</div>
                    </div>
                  </div>
                  
                  {analytics.top_genres && analytics.top_genres.length > 0 && (
                    <div className="top-genres">
                      <h3>Top Genres</h3>
                      <div className="genres-list">
                        {analytics.top_genres.map((genre, index) => (
                          <span key={index} className="genre-tag">
                            {genre}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {!analytics && !loading && (
                <div className="no-results">
                  <p>No analytics data available. Start rating movies to see your insights!</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        mode={authMode}
        onSwitchMode={() => setAuthMode(authMode === 'login' ? 'signup' : 'login')}
      />
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
