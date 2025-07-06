import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = 'http://localhost:5000';

function App() {
  const [recommendations, setRecommendations] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [movies, setMovies] = useState([]);
  const [filteredMovies, setFilteredMovies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('search');
  const [modelComparison, setModelComparison] = useState(null);
  const [availableModels, setAvailableModels] = useState([]);

  // Form state
  const [userId, setUserId] = useState(1);
  const [itemId, setItemId] = useState(1);
  const [numRecommendations, setNumRecommendations] = useState(10);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('title');
  const [selectedModel, setSelectedModel] = useState('ensemble');

  // Initialize data
  useEffect(() => {
    fetchMovies();
    fetchRandomMovies();
    fetchAvailableModels();
  }, []);

  // Handle search
  useEffect(() => {
    if (searchQuery && searchQuery.length > 2) {
      searchMovies();
    } else if (searchQuery.length === 0) {
      setFilteredMovies(sortMovies(movies.slice(0, 100), sortBy));
    }
  }, [searchQuery, sortBy]);

  // Fetch available models
  const fetchAvailableModels = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/models`);
      if (!response.ok) throw new Error('Failed to fetch models');
      const data = await response.json();
      setAvailableModels(data.available_models || []);
    } catch (err) {
      console.error('Error fetching models:', err);
    }
  };

  // Search movies via API
  const searchMovies = async () => {
    setSearchLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(searchQuery)}&sort=${sortBy}&limit=50`);
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
      const response = await fetch(`${API_BASE_URL}/movies/random?limit=50`);
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
          // Extract year from title if available
          const yearA = a.title.match(/\((\d{4})\)/)?.[1] || '0';
          const yearB = b.title.match(/\((\d{4})\)/)?.[1] || '0';
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
      const response = await fetch(`${API_BASE_URL}/movies`);
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

  // Fetch recommendations with model selection
  const fetchRecommendations = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE_URL}/recommendations/${userId}?n=${numRecommendations}&model=${selectedModel}`);
      if (!response.ok) throw new Error('Failed to fetch recommendations');
      const data = await response.json();
      setRecommendations(data.recommendations || []);
    } catch (err) {
      setError(`Error fetching recommendations: ${err.message}`);
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  // Compare models
  const compareModels = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE_URL}/compare/${userId}?n=${numRecommendations}`);
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

  // Predict rating with model selection
  const predictRating = async (userIdParam = userId, itemIdParam = itemId) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE_URL}/predict?user_id=${userIdParam}&item_id=${itemIdParam}&model=${selectedModel}`);
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

  // Generate star rating
  const generateStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    
    for (let i = 0; i < fullStars; i++) {
      stars.push(<span key={i} className="star">★</span>);
    }
    
    if (hasHalfStar) {
      stars.push(<span key="half" className="star">☆</span>);
    }
    
    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
      stars.push(<span key={`empty-${i}`} className="star empty">☆</span>);
    }
    
    return stars;
  };

  // Quick actions
  const handleQuickRecommend = (movieId) => {
    setItemId(movieId);
    setActiveTab('predict');
    predictRating(userId, movieId);
  };

  const handleQuickPredict = (movieId) => {
    setItemId(movieId);
    predictRating(userId, movieId);
  };

  // Model label mapping
  const getModelLabel = (model) => {
    const modelLabels = {
      'svd': 'SVD (Matrix Factorization)',
      'nmf': 'NMF (Non-negative Matrix Factorization)',
      'item_knn': 'Item-based Collaborative Filtering',
      'user_knn': 'User-based Collaborative Filtering',
      'content': 'Content-based Filtering',
      'ensemble': 'Ensemble (All Models Combined)'
    };
    return modelLabels[model] || model;
  };

  return (
    <div className="App">
      {/* Floating Background Elements */}
      <div className="floating-elements">
        <div className="floating-element"></div>
        <div className="floating-element"></div>
        <div className="floating-element"></div>
        <div className="floating-element"></div>
        <div className="floating-element"></div>
        <div className="floating-element"></div>
        <div className="floating-element"></div>
        <div className="floating-element"></div>
        <div className="floating-element"></div>
      </div>

      <header className="App-header">
        <h1 className="gradient-text">🎬 AI Movie Recommendation Engine</h1>
        <p>Discover your next favorite movie with advanced machine learning</p>
      </header>

      <div className="container">
        <div className="tabs">
          <button 
            className={activeTab === 'search' ? 'active' : ''}
            onClick={() => setActiveTab('search')}
          >
            🔍 Browse Movies
          </button>
          <button 
            className={activeTab === 'recommend' ? 'active' : ''}
            onClick={() => setActiveTab('recommend')}
          >
            🎯 Get Recommendations
          </button>
          <button 
            className={activeTab === 'compare' ? 'active' : ''}
            onClick={() => setActiveTab('compare')}
          >
            ⚖️ Compare Models
          </button>
          <button 
            className={activeTab === 'predict' ? 'active' : ''}
            onClick={() => setActiveTab('predict')}
          >
            🎲 Predict Rating
          </button>
        </div>

        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}

        {/* Model Selection */}
        <div className="model-selection">
          <label htmlFor="model-select">🧠 Select Model:</label>
          <select 
            id="model-select" 
            value={selectedModel} 
            onChange={(e) => setSelectedModel(e.target.value)}
            className="model-select"
          >
            {availableModels.map(model => (
              <option key={model} value={model}>
                {getModelLabel(model)}
              </option>
            ))}
          </select>
        </div>

        {activeTab === 'search' && (
          <div className="section">
            <h2 className="gradient-text">🎬 Browse Movies</h2>
            
            <div className="search-bar">
              <input
                type="text"
                placeholder="Search movies by title..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="search-input"
              />
              <select 
                value={sortBy} 
                onChange={(e) => setSortBy(e.target.value)}
                className="sort-select"
              >
                <option value="title">Sort by Title</option>
                <option value="year">Sort by Year</option>
                <option value="id">Sort by ID</option>
              </select>
            </div>

            {searchLoading && (
              <div className="loading">
                <div className="spinner"></div>
                <span>Searching movies...</span>
              </div>
            )}

            <div className="movies-grid">
              {filteredMovies.map(movie => (
                <div key={movie.id} className="movie-card interactive-element">
                  <div className="movie-title">{movie.title}</div>
                  <div className="movie-id">ID: {movie.id}</div>
                  {movie.year && movie.year > 0 && (
                    <div className="movie-year">Year: {movie.year}</div>
                  )}
                  <div className="movie-actions">
                    <button 
                      onClick={() => handleQuickRecommend(movie.id)}
                      className="action-btn recommend-btn"
                    >
                      🎯 Get Recommendations
                    </button>
                    <button 
                      onClick={() => handleQuickPredict(movie.id)}
                      className="action-btn predict-btn"
                    >
                      ⭐ Predict Rating
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'recommend' && (
          <div className="section">
            <h2 className="gradient-text">🎯 Get Personalized Recommendations</h2>
            
            <div className="form-row">
              <div className="form-group">
                <label>User ID (1-943):</label>
                <input
                  type="number"
                  value={userId}
                  onChange={(e) => setUserId(parseInt(e.target.value))}
                  min="1"
                  max="943"
                />
              </div>
              <div className="form-group">
                <label>Number of Recommendations:</label>
                <input
                  type="number"
                  value={numRecommendations}
                  onChange={(e) => setNumRecommendations(parseInt(e.target.value))}
                  min="1"
                  max="50"
                />
              </div>
            </div>

            <button 
              onClick={fetchRecommendations}
              disabled={loading}
              className="btn-primary"
            >
              {loading ? 'Loading...' : `Get Recommendations (${getModelLabel(selectedModel)})`}
            </button>

            {recommendations.length > 0 && (
              <div className="recommendations">
                <h3>📽️ Recommended Movies for User {userId}</h3>
                <div className="recommendations-grid">
                  {recommendations.map((movie, index) => (
                    <div key={movie.item_id} className="recommendation-card">
                      <div className="recommendation-rank">#{index + 1}</div>
                      <div className="recommendation-title">{movie.title}</div>
                      <div className="recommendation-details">
                        <div className="movie-rating">
                          <div className="rating-stars">
                            {generateStars(movie.predicted_rating)}
                          </div>
                          <span>{movie.predicted_rating}/5.0</span>
                        </div>
                        <div className="recommendation-model">
                          Model: {movie.model || selectedModel}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'compare' && (
          <div className="section">
            <h2 className="gradient-text">⚖️ Compare Recommendation Models</h2>
            
            <div className="form-row">
              <div className="form-group">
                <label>User ID (1-943):</label>
                <input
                  type="number"
                  value={userId}
                  onChange={(e) => setUserId(parseInt(e.target.value))}
                  min="1"
                  max="943"
                />
              </div>
              <div className="form-group">
                <label>Number of Recommendations:</label>
                <input
                  type="number"
                  value={numRecommendations}
                  onChange={(e) => setNumRecommendations(parseInt(e.target.value))}
                  min="1"
                  max="20"
                />
              </div>
            </div>

            <button 
              onClick={compareModels}
              disabled={loading}
              className="btn-primary"
            >
              {loading ? 'Comparing...' : 'Compare All Models'}
            </button>

            {modelComparison && (
              <div className="model-comparison">
                <h3>🔍 Model Comparison Results for User {userId}</h3>
                <div className="comparison-grid">
                  {Object.entries(modelComparison.comparison).map(([model, recs]) => (
                    <div key={model} className="comparison-section">
                      <h4 className="model-title">{getModelLabel(model)}</h4>
                      {recs.error ? (
                        <div className="error-message">
                          <span className="error-icon">❌</span>
                          {recs.error}
                        </div>
                      ) : (
                        <div className="comparison-recommendations">
                          {recs.slice(0, 5).map((movie, index) => (
                            <div key={movie.item_id} className="comparison-item">
                              <div className="comparison-rank">#{index + 1}</div>
                              <div className="comparison-title">{movie.title}</div>
                              <div className="comparison-rating">
                                <div className="rating-stars">
                                  {generateStars(movie.predicted_rating)}
                                </div>
                                <span>{movie.predicted_rating}/5.0</span>
                              </div>
                              {movie.model_scores && (
                                <div className="model-scores">
                                  {Object.entries(movie.model_scores).map(([modelName, score]) => (
                                    <div key={modelName} className="score-item">
                                      <span className="score-model">{modelName}:</span>
                                      <span className="score-value">{score.toFixed(2)}</span>
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'predict' && (
          <div className="section">
            <h2 className="gradient-text">⭐ Predict Movie Rating</h2>
            
            <div className="form-row">
              <div className="form-group">
                <label>User ID (1-943):</label>
                <input
                  type="number"
                  value={userId}
                  onChange={(e) => setUserId(parseInt(e.target.value))}
                  min="1"
                  max="943"
                />
              </div>
              <div className="form-group">
                <label>Movie ID (1-1682):</label>
                <input
                  type="number"
                  value={itemId}
                  onChange={(e) => setItemId(parseInt(e.target.value))}
                  min="1"
                  max="1682"
                />
              </div>
            </div>

            <button 
              onClick={() => predictRating()}
              disabled={loading}
              className="btn-primary"
            >
              {loading ? 'Predicting...' : `Predict Rating (${getModelLabel(selectedModel)})`}
            </button>

            {prediction && (
              <div className="prediction">
                <h3>🔮 Rating Prediction</h3>
                <div className="prediction-card">
                  <div className="prediction-movie">{prediction.title}</div>
                  <div className="prediction-rating">
                    <div className="prediction-rating-stars">
                      {generateStars(prediction.predicted_rating)}
                    </div>
                    <span>{prediction.predicted_rating}/5.0</span>
                  </div>
                  <div className="prediction-details">
                    <div>User {prediction.user_id} → Movie {prediction.item_id}</div>
                    <div>Model: {prediction.model || selectedModel}</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        <div className="section">
          <h2 className="gradient-text">📊 System Statistics</h2>
          <div className="stats-grid">
            <div className="stat-card interactive-element">
              <div className="stat-number">{movies.length}</div>
              <div className="stat-label">Movies Available</div>
            </div>
            <div className="stat-card interactive-element">
              <div className="stat-number">943</div>
              <div className="stat-label">Users in Dataset</div>
            </div>
            <div className="stat-card interactive-element">
              <div className="stat-number">100K</div>
              <div className="stat-label">Total Ratings</div>
            </div>
            <div className="stat-card interactive-element">
              <div className="stat-number">{availableModels.length}</div>
              <div className="stat-label">ML Models</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
