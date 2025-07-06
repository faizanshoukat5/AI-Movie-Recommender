import React from 'react';

const RecommendationsPage = ({ 
  recommendations, 
  loading, 
  userId, 
  setUserId, 
  numRecommendations, 
  setNumRecommendations, 
  selectedModel, 
  setSelectedModel, 
  availableModels, 
  handleGetRecommendations,
  MovieCard,
  error 
}) => {
  return (
    <div className="space-y-6">
      {/* Recommendations Form */}
      <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
        <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
          🎯 Get Personalized Recommendations
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
            <label className="block text-sm font-medium text-gray-300 mb-2">Number of Movies</label>
            <input
              type="number"
              min="1"
              max="50"
              value={numRecommendations}
              onChange={(e) => setNumRecommendations(parseInt(e.target.value))}
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
              onClick={handleGetRecommendations}
              disabled={loading}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 text-white font-semibold py-2 px-4 rounded-lg transition-all duration-200 transform hover:scale-105"
            >
              {loading ? 'Loading...' : 'Get Recommendations'}
            </button>
          </div>
        </div>
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
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400"></div>
          <span className="ml-3 text-white">Getting recommendations...</span>
        </div>
      )}

      {/* Recommendations Results */}
      {!loading && recommendations.length > 0 && (
        <div>
          <h3 className="text-xl font-semibold text-white mb-6">
            Recommendations for User {userId} ({recommendations.length} movies)
          </h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
            {recommendations.map((movie) => (
              <MovieCard key={movie.id} movie={movie} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default RecommendationsPage;
