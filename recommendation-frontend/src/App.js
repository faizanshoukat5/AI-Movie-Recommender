import React, { useState, useEffect } from 'react';

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
      const url = `${API_BASE_URL}/predict?user_id=${userIdParam}&item_id=${itemIdParam}&model=${selectedModel}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to predict rating: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }
      
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
      stars.push(<span key={i} className="text-yellow-400">★</span>);
    }
    
    if (hasHalfStar) {
      stars.push(<span key="half" className="text-yellow-400">☆</span>);
    }
    
    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
      stars.push(<span key={`empty-${i}`} className="text-gray-300">☆</span>);
    }
    
    return stars;
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

  // Tab content components
  const TabButton = ({ id, label, icon, active, onClick }) => (
    <button
      onClick={() => onClick(id)}
      className={`
        flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200
        ${active 
          ? 'bg-white text-purple-900 shadow-lg' 
          : 'text-white/80 hover:text-white hover:bg-white/10'
        }
      `}
    >
      <span className="text-lg">{icon}</span>
      <span>{label}</span>
    </button>
  );

  const LoadingSpinner = () => (
    <div className="flex items-center justify-center py-12">
      <div className="relative">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-white/20 border-t-white"></div>
        <div className="absolute inset-0 animate-ping rounded-full h-12 w-12 border-4 border-white/40"></div>
      </div>
      <span className="ml-3 text-white animate-pulse">Loading...</span>
    </div>
  );

  const ErrorMessage = ({ message }) => (
    <div className="bg-red-500/20 backdrop-blur-sm border border-red-500/50 rounded-lg p-4 mb-6 animate-pulse">
      <div className="flex items-center">
        <span className="text-red-400 text-xl mr-2">⚠️</span>
        <span className="text-red-200">{message}</span>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0">
          <div className="absolute inset-0 opacity-20"></div>
        </div>
        
        <div className="relative container mx-auto px-6 py-16">
          <div className="text-center">
            <h1 className="text-5xl md:text-7xl font-bold bg-gradient-to-r from-white via-purple-200 to-blue-200 bg-clip-text text-transparent mb-4">
              🎬 AI Movie Recommender
            </h1>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Discover your next favorite movie with advanced machine learning algorithms
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-4">
              <div className="bg-white/10 backdrop-blur-sm rounded-lg px-4 py-2">
                <span className="text-white font-medium">6 ML Models</span>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-lg px-4 py-2">
                <span className="text-white font-medium">1,682 Movies</span>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-lg px-4 py-2">
                <span className="text-white font-medium">100K Ratings</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 pb-12">
        {/* Model Selection */}
        <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 mb-8 border border-white/20">
          <div className="flex flex-col sm:flex-row items-center gap-4">
            <label className="text-white font-medium flex items-center">
              <span className="text-2xl mr-2">🧠</span>
              Select AI Model:
            </label>
            <select 
              value={selectedModel} 
              onChange={(e) => setSelectedModel(e.target.value)}
              className="flex-1 sm:max-w-md bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-400"
            >
              {availableModels.map(model => (
                <option key={model} value={model} className="bg-slate-800 text-white">
                  {getModelLabel(model)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap gap-2 mb-8 bg-white/10 backdrop-blur-sm rounded-2xl p-2 border border-white/20">
          <TabButton 
            id="search" 
            label="Browse Movies" 
            icon="🔍" 
            active={activeTab === 'search'} 
            onClick={setActiveTab} 
          />
          <TabButton 
            id="recommend" 
            label="Get Recommendations" 
            icon="🎯" 
            active={activeTab === 'recommend'} 
            onClick={setActiveTab} 
          />
          <TabButton 
            id="compare" 
            label="Compare Models" 
            icon="⚖️" 
            active={activeTab === 'compare'} 
            onClick={setActiveTab} 
          />
          <TabButton 
            id="predict" 
            label="Predict Rating" 
            icon="🎲" 
            active={activeTab === 'predict'} 
            onClick={setActiveTab} 
          />
        </div>

        {/* Error Display */}
        {error && <ErrorMessage message={error} />}

        {/* Tab Content */}
        <div className="bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 overflow-hidden">
          
          {/* Browse Movies Tab */}
          {activeTab === 'search' && (
            <div className="p-8">
              <h2 className="text-3xl font-bold text-white mb-6 flex items-center">
                <span className="text-4xl mr-3">🎬</span>
                Browse Movies
              </h2>
              
              {/* Search Controls */}
              <div className="flex flex-col sm:flex-row gap-4 mb-8">
                <div className="flex-1">
                  <input
                    type="text"
                    placeholder="Search movies by title..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg px-4 py-3 text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-400"
                  />
                </div>
                <select 
                  value={sortBy} 
                  onChange={(e) => setSortBy(e.target.value)}
                  className="bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-400"
                >
                  <option value="title" className="bg-slate-800">Sort by Title</option>
                  <option value="year" className="bg-slate-800">Sort by Year</option>
                  <option value="id" className="bg-slate-800">Sort by ID</option>
                </select>
              </div>

              {searchLoading && <LoadingSpinner />}

              {/* Movies Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {filteredMovies.map(movie => (
                  <div key={movie.id} className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 hover:bg-white/20 hover:border-white/40 hover:shadow-lg hover:shadow-purple-500/20 transition-all duration-300 group transform hover:-translate-y-1">
                    <div className="flex items-start justify-between mb-4">
                      <h3 className="font-semibold text-white group-hover:text-purple-200 transition-colors line-clamp-2">
                        {movie.title}
                      </h3>
                      <span className="text-sm text-gray-300 bg-white/10 px-2 py-1 rounded group-hover:bg-white/20 transition-colors">
                        #{movie.id}
                      </span>
                    </div>
                    
                    {movie.year && movie.year > 0 && (
                      <div className="text-sm text-gray-300 mb-4">
                        📅 {movie.year}
                      </div>
                    )}
                    
                    <div className="flex gap-2">
                      <button 
                        onClick={() => {
                          setItemId(movie.id);
                          setActiveTab('predict');
                          predictRating(userId, movie.id);
                        }}
                        className="flex-1 bg-purple-600 hover:bg-purple-700 text-white text-sm py-2 px-3 rounded-lg transition-colors"
                      >
                        ⭐ Predict
                      </button>
                      <button 
                        onClick={() => {
                          setItemId(movie.id);
                          setActiveTab('recommend');
                        }}
                        className="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-sm py-2 px-3 rounded-lg transition-colors"
                      >
                        🎯 Recommend
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Get Recommendations Tab */}
          {activeTab === 'recommend' && (
            <div className="p-8">
              <h2 className="text-3xl font-bold text-white mb-6 flex items-center">
                <span className="text-4xl mr-3">🎯</span>
                Get Personalized Recommendations
              </h2>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-8">
                <div>
                  <label className="block text-white font-medium mb-2">User ID (1-943):</label>
                  <input
                    type="number"
                    value={userId}
                    onChange={(e) => setUserId(parseInt(e.target.value))}
                    min="1"
                    max="943"
                    className="w-full bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-400"
                  />
                </div>
                <div>
                  <label className="block text-white font-medium mb-2">Number of Recommendations:</label>
                  <input
                    type="number"
                    value={numRecommendations}
                    onChange={(e) => setNumRecommendations(parseInt(e.target.value))}
                    min="1"
                    max="50"
                    className="w-full bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-400"
                  />
                </div>
              </div>

              <button 
                onClick={fetchRecommendations}
                disabled={loading}
                className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 text-white font-semibold py-3 px-8 rounded-lg transition-all duration-200 mb-8"
              >
                {loading ? (
                  <span className="flex items-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Loading...
                  </span>
                ) : (
                  `Get Recommendations (${getModelLabel(selectedModel)})`
                )}
              </button>

              {recommendations.length > 0 && (
                <div>
                  <h3 className="text-2xl font-bold text-white mb-6">
                    📽️ Recommended Movies for User {userId}
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {recommendations.map((movie, index) => (
                      <div key={movie.item_id} className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/20 relative hover:shadow-lg hover:shadow-purple-500/20 transition-all duration-300 transform hover:-translate-y-1 animate-fade-in" style={{ animationDelay: `${index * 0.1}s` }}>
                        <div className="absolute -top-3 -right-3 bg-gradient-to-r from-yellow-400 to-orange-500 text-black text-sm font-bold w-8 h-8 rounded-full flex items-center justify-center shadow-lg">
                          #{index + 1}
                        </div>
                        <h4 className="font-semibold text-white mb-4 line-clamp-2">
                          {movie.title}
                        </h4>
                        <div className="space-y-3">
                          <div className="flex items-center gap-2">
                            <span className="text-lg">{generateStars(movie.predicted_rating)}</span>
                            <span className="text-white font-medium">{movie.predicted_rating}/5.0</span>
                          </div>
                          <div className="text-sm text-gray-300 bg-white/10 px-3 py-1 rounded-full inline-block">
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

          {/* Compare Models Tab */}
          {activeTab === 'compare' && (
            <div className="p-8">
              <h2 className="text-3xl font-bold text-white mb-6 flex items-center">
                <span className="text-4xl mr-3">⚖️</span>
                Compare Recommendation Models
              </h2>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-8">
                <div>
                  <label className="block text-white font-medium mb-2">User ID (1-943):</label>
                  <input
                    type="number"
                    value={userId}
                    onChange={(e) => setUserId(parseInt(e.target.value))}
                    min="1"
                    max="943"
                    className="w-full bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-400"
                  />
                </div>
                <div>
                  <label className="block text-white font-medium mb-2">Number of Recommendations:</label>
                  <input
                    type="number"
                    value={numRecommendations}
                    onChange={(e) => setNumRecommendations(parseInt(e.target.value))}
                    min="1"
                    max="20"
                    className="w-full bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-400"
                  />
                </div>
              </div>

              <button 
                onClick={compareModels}
                disabled={loading}
                className="bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700 disabled:opacity-50 text-white font-semibold py-3 px-8 rounded-lg transition-all duration-200 mb-8"
              >
                {loading ? (
                  <span className="flex items-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Comparing...
                  </span>
                ) : (
                  'Compare All Models'
                )}
              </button>

              {modelComparison && (
                <div>
                  <h3 className="text-2xl font-bold text-white mb-6">
                    🔍 Model Comparison Results for User {userId}
                  </h3>
                  <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                    {Object.entries(modelComparison.comparison).map(([model, recs]) => (
                      <div key={model} className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm rounded-xl border border-white/20 overflow-hidden">
                        <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-4">
                          <h4 className="text-lg font-bold text-white text-center">
                            {getModelLabel(model)}
                          </h4>
                        </div>
                        <div className="p-4">
                          {recs.error ? (
                            <div className="text-red-300 text-center py-4">
                              <span className="text-2xl">❌</span>
                              <p className="mt-2">{recs.error}</p>
                            </div>
                          ) : (
                            <div className="space-y-3">
                              {recs.slice(0, 5).map((movie, index) => (
                                <div key={movie.item_id} className="bg-white/10 rounded-lg p-3">
                                  <div className="flex items-center justify-between mb-2">
                                    <span className="text-xs text-yellow-400 font-medium">#{index + 1}</span>
                                    <div className="flex items-center gap-1">
                                      {generateStars(movie.predicted_rating)}
                                      <span className="text-xs text-white ml-1">
                                        {movie.predicted_rating}
                                      </span>
                                    </div>
                                  </div>
                                  <h5 className="text-sm text-white font-medium line-clamp-2">
                                    {movie.title}
                                  </h5>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Predict Rating Tab */}
          {activeTab === 'predict' && (
            <div className="p-8">
              <h2 className="text-3xl font-bold text-white mb-6 flex items-center">
                <span className="text-4xl mr-3">⭐</span>
                Predict Movie Rating
              </h2>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-8">
                <div>
                  <label className="block text-white font-medium mb-2">User ID (1-943):</label>
                  <input
                    type="number"
                    value={userId}
                    onChange={(e) => setUserId(parseInt(e.target.value))}
                    min="1"
                    max="943"
                    className="w-full bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-400"
                  />
                </div>
                <div>
                  <label className="block text-white font-medium mb-2">Movie ID (1-1682):</label>
                  <input
                    type="number"
                    value={itemId}
                    onChange={(e) => setItemId(parseInt(e.target.value))}
                    min="1"
                    max="1682"
                    className="w-full bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-400"
                  />
                </div>
              </div>

              <button 
                onClick={() => predictRating()}
                disabled={loading}
                className="bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 disabled:opacity-50 text-white font-semibold py-3 px-8 rounded-lg transition-all duration-200 mb-8"
              >
                {loading ? (
                  <span className="flex items-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Predicting...
                  </span>
                ) : (
                  `Predict Rating (${getModelLabel(selectedModel)})`
                )}
              </button>

              {prediction && (
                <div className="max-w-md mx-auto">
                  <h3 className="text-2xl font-bold text-white mb-6 text-center">
                    🔮 Rating Prediction
                  </h3>
                  <div className="bg-gradient-to-br from-white/20 to-white/10 backdrop-blur-sm rounded-xl p-8 border border-white/20 text-center">
                    <h4 className="text-xl font-semibold text-white mb-4">
                      {prediction.title}
                    </h4>
                    <div className="mb-6">
                      <div className="flex justify-center items-center gap-2 mb-2">
                        <span className="text-3xl">{generateStars(prediction.predicted_rating)}</span>
                      </div>
                      <span className="text-2xl font-bold text-white">
                        {prediction.predicted_rating}/5.0
                      </span>
                    </div>
                    <div className="space-y-2 text-gray-300">
                      <div>User {prediction.user_id} → Movie {prediction.item_id}</div>
                      <div className="bg-white/10 px-3 py-1 rounded-full inline-block text-sm">
                        Model: {prediction.model || selectedModel}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer Stats */}
        <div className="mt-12 grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 text-center">
            <div className="text-3xl font-bold text-white mb-2">{movies.length}</div>
            <div className="text-gray-300">Movies Available</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 text-center">
            <div className="text-3xl font-bold text-white mb-2">943</div>
            <div className="text-gray-300">Users in Dataset</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 text-center">
            <div className="text-3xl font-bold text-white mb-2">100K</div>
            <div className="text-gray-300">Total Ratings</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 text-center">
            <div className="text-3xl font-bold text-white mb-2">{availableModels.length}</div>
            <div className="text-gray-300">ML Models</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
