import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import './UserProfile.css';

const UserProfile = () => {
  const { currentUser, userProfile, logout, updateUserPreferences, loading } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [favoriteGenres, setFavoriteGenres] = useState([]);

  // Update favoriteGenres when userProfile changes
  useEffect(() => {
    if (userProfile?.preferences?.favoriteGenres) {
      setFavoriteGenres(userProfile.preferences.favoriteGenres);
    }
  }, [userProfile]);

  const genres = [
    'Action', 'Adventure', 'Comedy', 'Drama', 'Horror', 'Romance', 
    'Sci-Fi', 'Thriller', 'Animation', 'Documentary', 'Fantasy', 
    'Mystery', 'Crime', 'Family', 'Musical', 'War', 'Western'
  ];

  const handleGenreToggle = (genre) => {
    setFavoriteGenres(prev => 
      prev.includes(genre) 
        ? prev.filter(g => g !== genre)
        : [...prev, genre]
    );
  };

  const handleSavePreferences = async () => {
    await updateUserPreferences({ favoriteGenres });
    setIsEditing(false);
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  // Show loading state while authentication is loading
  if (loading) {
    return (
      <div className="user-profile-loading">
        <div className="loading-spinner">🔄</div>
        <p>Loading your profile...</p>
      </div>
    );
  }

  // Show login required message if not authenticated
  if (!currentUser) {
    return (
      <div className="user-profile-not-authenticated">
        <div className="not-auth-content">
          <span className="not-auth-icon">🔒</span>
          <h2>Authentication Required</h2>
          <p>Please sign in to view your profile</p>
          <button 
            onClick={() => window.history.back()}
            className="back-btn"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  // Show profile loading if user is authenticated but profile is still loading
  if (currentUser && !userProfile) {
    return (
      <div className="user-profile-loading">
        <div className="loading-spinner">⏳</div>
        <p>Setting up your profile...</p>
      </div>
    );
  }

  return (
    <div className="user-profile">
      <div className="profile-header">
        <div className="profile-avatar">
          {userProfile.photoURL ? (
            <img src={userProfile.photoURL} alt="Profile" />
          ) : (
            <div className="avatar-placeholder">
              {userProfile.displayName?.charAt(0).toUpperCase() || 'U'}
            </div>
          )}
        </div>
        
        <div className="profile-info">
          <h2>{userProfile.displayName || 'Movie Enthusiast'}</h2>
          <p className="profile-email">{currentUser.email}</p>
          <p className="profile-joined">
            Joined {new Date(userProfile.stats?.joinDate).toLocaleDateString()}
          </p>
        </div>
        
        <button onClick={handleLogout} className="logout-btn">
          <span className="logout-icon">👋</span>
          Sign Out
        </button>
      </div>

      <div className="profile-stats">
        <div className="stat-card">
          <div className="stat-number">{userProfile.stats?.totalRatings || 0}</div>
          <div className="stat-label">Movies Rated</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-number">{userProfile.preferences?.watchlist?.length || 0}</div>
          <div className="stat-label">Watchlist</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-number">{userProfile.preferences?.favorites?.length || 0}</div>
          <div className="stat-label">Favorites</div>
        </div>
      </div>

      <div className="profile-section">
        <div className="section-header">
          <h3>🎭 Favorite Genres</h3>
          <button 
            onClick={() => setIsEditing(!isEditing)}
            className="edit-btn"
          >
            {isEditing ? 'Cancel' : 'Edit'}
          </button>
        </div>

        {isEditing ? (
          <div className="genre-editor">
            <div className="genres-grid">
              {genres.map(genre => (
                <button
                  key={genre}
                  onClick={() => handleGenreToggle(genre)}
                  className={`genre-btn ${favoriteGenres.includes(genre) ? 'selected' : ''}`}
                >
                  {genre}
                </button>
              ))}
            </div>
            
            <div className="editor-actions">
              <button onClick={handleSavePreferences} className="save-btn">
                Save Preferences
              </button>
            </div>
          </div>
        ) : (
          <div className="genres-display">
            {userProfile.preferences?.favoriteGenres?.length > 0 ? (
              <div className="genres-list">
                {userProfile.preferences.favoriteGenres.map(genre => (
                  <span key={genre} className="genre-tag">{genre}</span>
                ))}
              </div>
            ) : (
              <p className="no-genres">No favorite genres selected yet.</p>
            )}
          </div>
        )}
      </div>

      <div className="profile-section">
        <h3>📚 My Watchlist</h3>
        
        {userProfile.preferences?.watchlist?.length > 0 ? (
          <div className="watchlist-grid">
            {userProfile.preferences.watchlist.slice(0, 6).map(movie => (
              <div key={movie.id} className="watchlist-item">
                <div className="movie-poster">
                  {movie.poster_url ? (
                    <img src={movie.poster_url} alt={movie.title} />
                  ) : (
                    <div className="poster-placeholder">🎬</div>
                  )}
                </div>
                <div className="movie-info">
                  <h4>{movie.title}</h4>
                  <p>Added {new Date(movie.addedAt).toLocaleDateString()}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-watchlist">
            <span className="empty-icon">📝</span>
            <p>Your watchlist is empty. Start adding movies!</p>
          </div>
        )}
      </div>

      <div className="profile-section">
        <h3>⭐ Recent Ratings</h3>
        
        {userProfile.preferences?.ratings && Object.keys(userProfile.preferences.ratings).length > 0 ? (
          <div className="ratings-list">
            {Object.entries(userProfile.preferences.ratings)
              .sort((a, b) => new Date(b[1].ratedAt) - new Date(a[1].ratedAt))
              .slice(0, 5)
              .map(([movieId, rating]) => (
                <div key={movieId} className="rating-item">
                  {rating.moviePoster && (
                    <div className="rating-movie-poster">
                      <img 
                        src={rating.moviePoster} 
                        alt={rating.movieTitle || `Movie ${movieId}`}
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                    </div>
                  )}
                  {!rating.moviePoster && (
                    <div className="rating-movie-poster">
                      <div className="poster-placeholder">
                        🎬
                      </div>
                    </div>
                  )}
                  <div className="rating-content">
                    <div className="rating-movie-info">
                      <h4>{rating.movieTitle || `Movie ${movieId}`}</h4>
                      <div className="rating-stars">
                        {'⭐'.repeat(Math.floor(rating.rating))}
                        <span className="rating-score">{rating.rating}/5</span>
                      </div>
                    </div>
                    <div className="rating-meta">
                      <span className="rating-date">
                        Rated {new Date(rating.ratedAt).toLocaleDateString()}
                      </span>
                      {rating.review && (
                        <p className="rating-review">"{rating.review}"</p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
          </div>
        ) : (
          <div className="empty-ratings">
            <span className="empty-icon">⭐</span>
            <p>No ratings yet. Start rating movies to build your profile!</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserProfile;
