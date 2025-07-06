import React, { useEffect } from 'react';
import { useAuth } from '../AuthContext';

const MyRatingsPage = ({ 
  userRatings, 
  movies, 
  userId, 
  handleRateMovie, 
  showRatingModal, 
  setShowRatingModal, 
  selectedMovieForRating,
  setSelectedMovieForRating,
  RatingModal 
}) => {
  const { currentUser, userProfile } = useAuth();
  
  // Real-time sync: Re-render when userProfile changes
  useEffect(() => {
    if (currentUser && userProfile) {
      console.log('User profile updated, ratings synced');
    }
  }, [currentUser, userProfile]);
  
  // Use Firebase ratings if user is logged in, otherwise use local ratings
  const ratingsToDisplay = currentUser && userProfile?.preferences?.ratings 
    ? userProfile.preferences.ratings 
    : userRatings;
  
  // Convert Firebase rating format to display format
  const formatRatingsForDisplay = (ratings) => {
    if (currentUser && userProfile?.preferences?.ratings) {
      // Firebase format: { movieId: { rating, review, ratedAt, movieTitle, moviePoster } }
      return Object.entries(ratings).reduce((acc, [movieId, ratingData]) => {
        acc[movieId] = ratingData.rating;
        return acc;
      }, {});
    }
    // Local format: { movieId: rating }
    return ratings;
  };
  
  const displayRatings = formatRatingsForDisplay(ratingsToDisplay);
  return (
    <div className="space-y-6">
      <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
        <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
          ⭐ My Ratings
        </h2>
        <p className="text-gray-300 mb-6">
          📽️ You've rated {Object.keys(displayRatings).length} movies
        </p>
        
        {Object.keys(displayRatings).length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">⭐</div>
            <h3 className="text-xl font-semibold text-white mb-2">No ratings yet</h3>
            <p className="text-gray-300">Start rating movies to see them here!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {Object.entries(displayRatings)
              .sort((a, b) => {
                // Sort by rating date if available (Firebase), otherwise by rating value
                if (currentUser && userProfile?.preferences?.ratings) {
                  const ratingA = userProfile.preferences.ratings[a[0]];
                  const ratingB = userProfile.preferences.ratings[b[0]];
                  return new Date(ratingB?.ratedAt || 0) - new Date(ratingA?.ratedAt || 0);
                }
                return b[1] - a[1]; // Sort by rating value for local ratings
              })
              .map(([movieId, rating]) => {
              const firebaseRatingData = currentUser && userProfile?.preferences?.ratings?.[movieId];
              const movieData = movies.find(m => m.id === parseInt(movieId));
              const movie = { 
                id: parseInt(movieId), 
                title: firebaseRatingData?.movieTitle || movieData?.title || `Movie ${movieId}`,
                poster_url: firebaseRatingData?.moviePoster || movieData?.poster_url
              };
              
              return (
                <div key={movieId} className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-300">
                  {/* Movie Poster */}
                  {movie.poster_url ? (
                    <div className="aspect-[2/3] overflow-hidden rounded-lg mb-4">
                      <img 
                        src={movie.poster_url}
                        alt={movie.title}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.target.parentElement.innerHTML = `
                            <div class="w-full h-full bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center rounded-lg">
                              <span class="text-gray-400 text-4xl">🎬</span>
                            </div>
                          `;
                        }}
                      />
                    </div>
                  ) : (
                    <div className="aspect-[2/3] bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center rounded-lg mb-4">
                      <span className="text-gray-400 text-4xl">🎬</span>
                    </div>
                  )}
                  
                  <h4 className="font-semibold text-white mb-4 line-clamp-2">
                    {movie.title}
                  </h4>
                  <div className="flex items-center justify-between">
                    <div className="flex">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <span key={star} className={`text-lg ${star <= rating ? 'text-yellow-400' : 'text-gray-500'}`}>
                          ★
                        </span>
                      ))}
                    </div>
                    <button
                      onClick={() => {
                        setSelectedMovieForRating(movie);
                        setShowRatingModal(true);
                      }}
                      className="text-sm bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded-md transition-colors"
                    >
                      Edit
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

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
  );
};

export default MyRatingsPage;
