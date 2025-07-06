import React from 'react';

const PredictRatingPage = ({ 
  prediction, 
  loading, 
  userId, 
  setUserId, 
  itemId, 
  setItemId, 
  selectedModel, 
  setSelectedModel, 
  availableModels, 
  handlePredictRating,
  movies,
  error 
}) => {
  const selectedMovie = movies.find(movie => movie.id === itemId);

  return (
    <div className="space-y-6">
      {/* Prediction Form */}
      <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
        <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
          🔮 Predict Rating
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">User ID</label>
            <input
              type="number"
              min="1"
              max="943"
              value={userId}
              onChange={(e) => setUserId(parseInt(e.target.value))}
              className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Movie ID</label>
            <input
              type="number"
              min="1"
              max="1682"
              value={itemId}
              onChange={(e) => setItemId(parseInt(e.target.value))}
              className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Model</label>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              {availableModels.map(model => (
                <option key={model} value={model} className="bg-gray-800">{model.toUpperCase()}</option>
              ))}
            </select>
          </div>
          
          <div className="flex items-end">
            <button
              onClick={handlePredictRating}
              disabled={loading}
              className="w-full bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 disabled:opacity-50 text-white font-semibold py-2 px-4 rounded-lg transition-all duration-200 transform hover:scale-105"
            >
              {loading ? 'Predicting...' : 'Predict Rating'}
            </button>
          </div>
        </div>

        {/* Selected Movie Preview */}
        {selectedMovie && (
          <div className="mt-4 p-4 bg-white/10 rounded-lg border border-white/20">
            <h4 className="text-white font-semibold mb-2">Selected Movie:</h4>
            <div className="flex items-center gap-4">
              {selectedMovie.poster_url && (
                <img 
                  src={selectedMovie.poster_url} 
                  alt={selectedMovie.title}
                  className="w-16 h-24 object-cover rounded"
                />
              )}
              <div>
                <p className="text-white font-medium">{selectedMovie.title}</p>
                <p className="text-gray-300 text-sm">ID: {selectedMovie.id}</p>
                {selectedMovie.genres && (
                  <p className="text-gray-400 text-sm">{selectedMovie.genres}</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4 text-red-200">
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-400"></div>
          <span className="ml-3 text-white">Predicting rating...</span>
        </div>
      )}

      {/* Prediction Result */}
      {!loading && prediction && (
        <div className="bg-gradient-to-br from-green-500/20 to-blue-500/20 backdrop-blur-sm rounded-xl p-6 border border-green-500/30">
          <h3 className="text-xl font-bold text-white mb-4">Prediction Result</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-300">User ID:</span>
                <span className="text-white font-semibold">{prediction.user_id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">Movie ID:</span>
                <span className="text-white font-semibold">{prediction.item_id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">Model Used:</span>
                <span className="text-white font-semibold">{prediction.model.toUpperCase()}</span>
              </div>
            </div>
            
            <div className="flex items-center justify-center">
              <div className="text-center">
                <div className="text-4xl font-bold text-green-400 mb-2">
                  {prediction.predicted_rating.toFixed(2)}
                </div>
                <div className="text-gray-300">Predicted Rating</div>
                <div className="flex justify-center mt-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <span 
                      key={star} 
                      className={`text-xl ${star <= Math.round(prediction.predicted_rating) ? 'text-yellow-400' : 'text-gray-500'}`}
                    >
                      ★
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PredictRatingPage;
