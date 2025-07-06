import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = 'http://localhost:5000';

function App() {
  const [recommendations, setRecommendations] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('recommendations');

  // Form state
  const [userId, setUserId] = useState(1);
  const [itemId, setItemId] = useState(1);
  const [numRecommendations, setNumRecommendations] = useState(10);

  // Initialize data
  useEffect(() => {
    fetchMovies();
    fetchRecommendations();
  }, []);

  // Fetch movies
  const fetchMovies = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/movies`);
      if (!response.ok) throw new Error('Failed to fetch movies');
      const data = await response.json();
      setMovies(data.movies || []);
    } catch (err) {
      setError(`Error fetching movies: ${err.message}`);
    }
  };

  // Fetch recommendations
  const fetchRecommendations = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE_URL}/recommendations/${userId}?n=${numRecommendations}`);
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

  // Predict rating
  const predictRating = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE_URL}/predict?user_id=${userId}&item_id=${itemId}`);
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

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎬 AI Movie Recommendation Engine</h1>
        <p>Discover your next favorite movie with machine learning</p>
      </header>

      <div className="container">
        <div className="tabs">
          <button 
            className={activeTab === 'recommendations' ? 'active' : ''}
            onClick={() => setActiveTab('recommendations')}
          >
            Get Recommendations
          </button>
          <button 
            className={activeTab === 'predict' ? 'active' : ''}
            onClick={() => setActiveTab('predict')}
          >
            Predict Rating
          </button>
          <button 
            className={activeTab === 'movies' ? 'active' : ''}
            onClick={() => setActiveTab('movies')}
          >
            Browse Movies
          </button>
        </div>

        {error && <div className="error">{error}</div>}

        {activeTab === 'recommendations' && (
          <div className="section">
            <h2>Get Movie Recommendations</h2>
            <div className="form-group">
              <label>User ID:</label>
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
            <button 
              onClick={fetchRecommendations}
              disabled={loading}
              className="btn-primary"
            >
              {loading ? 'Loading...' : 'Get Recommendations'}
            </button>

            {recommendations.length > 0 && (
              <div className="recommendations">
                <h3>Recommended Movies for User {userId}:</h3>
                <div className="movie-grid">
                  {recommendations.map((movie, index) => (
                    <div key={movie.item_id} className="movie-card">
                      <div className="movie-rank">#{index + 1}</div>
                      <div className="movie-title">{movie.title}</div>
                      <div className="movie-rating">
                        Predicted Rating: {movie.predicted_rating}/5
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'predict' && (
          <div className="section">
            <h2>Predict Movie Rating</h2>
            <div className="form-group">
              <label>User ID:</label>
              <input
                type="number"
                value={userId}
                onChange={(e) => setUserId(parseInt(e.target.value))}
                min="1"
                max="943"
              />
            </div>
            <div className="form-group">
              <label>Movie ID:</label>
              <input
                type="number"
                value={itemId}
                onChange={(e) => setItemId(parseInt(e.target.value))}
                min="1"
                max="1682"
              />
            </div>
            <button 
              onClick={predictRating}
              disabled={loading}
              className="btn-primary"
            >
              {loading ? 'Predicting...' : 'Predict Rating'}
            </button>

            {prediction && (
              <div className="prediction">
                <h3>Rating Prediction:</h3>
                <div className="prediction-card">
                  <div className="prediction-movie">{prediction.title}</div>
                  <div className="prediction-rating">
                    Predicted Rating: {prediction.predicted_rating}/5
                  </div>
                  <div className="prediction-details">
                    User {prediction.user_id} → Movie {prediction.item_id}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'movies' && (
          <div className="section">
            <h2>Browse Movies</h2>
            <div className="movie-count">
              Total Movies: {movies.length}
            </div>
            <div className="movie-list">
              {movies.slice(0, 100).map((movie) => (
                <div key={movie.id} className="movie-item">
                  <span className="movie-id">#{movie.id}</span>
                  <span className="movie-title">{movie.title}</span>
                </div>
              ))}
              {movies.length > 100 && (
                <div className="more-movies">
                  ... and {movies.length - 100} more movies
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
