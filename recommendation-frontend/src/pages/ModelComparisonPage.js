import React from 'react';

const ModelComparisonPage = ({ 
  modelComparison, 
  loading, 
  userId, 
  setUserId, 
  handleCompareModels,
  error 
}) => {
  return (
    <div className="space-y-6">
      {/* Model Comparison Form */}
      <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
        <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
          📊 Model Comparison
        </h2>
        
        <div className="flex flex-col md:flex-row gap-4 mb-4">
          <div className="md:w-48">
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
          
          <div className="flex items-end">
            <button
              onClick={handleCompareModels}
              disabled={loading}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 text-white font-semibold py-2 px-6 rounded-lg transition-all duration-200 transform hover:scale-105"
            >
              {loading ? 'Comparing...' : 'Compare Models'}
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
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
          <span className="ml-3 text-white">Comparing models...</span>
        </div>
      )}

      {/* Model Comparison Results */}
      {!loading && modelComparison && modelComparison.comparison && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {Object.entries(modelComparison.comparison).map(([modelName, data]) => (
            <div key={modelName} className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/20">
              <h3 className="text-xl font-bold text-white mb-4 capitalize">
                {modelName.replace('_', ' ')} Model
              </h3>
              
              {!Array.isArray(data) ? (
                <p className="text-red-400">Error: Invalid data format</p>
              ) : (
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-300 mb-2">Top Recommendations:</p>
                    <div className="space-y-2">
                      {data && data.length > 0 ? (
                        data.slice(0, 5).map((movie, index) => (
                          <div key={movie.item_id} className="flex justify-between items-center bg-white/10 rounded-lg p-3">
                            <div>
                              <span className="text-white font-medium">#{index + 1}</span>
                              <span className="text-gray-300 ml-2">{movie.title}</span>
                            </div>
                            <span className="text-purple-400 font-semibold">
                              {movie.predicted_rating.toFixed(2)}
                            </span>
                          </div>
                        ))
                      ) : (
                        <p className="text-gray-400">No recommendations available</p>
                      )}
                    </div>
                  </div>
                  
                  {data && data.length > 0 && (
                    <div className="pt-4 border-t border-white/20">
                      <p className="text-sm text-gray-300">
                        <span className="text-white font-semibold">Average Predicted Rating:</span> {' '}
                        {(data.reduce((sum, movie) => sum + movie.predicted_rating, 0) / data.length).toFixed(2)}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ModelComparisonPage;
