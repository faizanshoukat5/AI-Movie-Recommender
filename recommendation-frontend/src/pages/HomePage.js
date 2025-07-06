import React from 'react';

const HomePage = ({ 
  filteredMovies, 
  loading, 
  searchLoading, 
  searchQuery, 
  setSearchQuery, 
  sortBy, 
  setSortBy,
  MovieCard,
  error 
}) => {
  return (
    <div className="space-y-6">
      {/* Search and Filter Section */}
      <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
        <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
          🔍 Discover Movies
        </h2>
        
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search for movies..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent backdrop-blur-sm"
            />
          </div>
          
          <div className="md:w-48">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent backdrop-blur-sm"
            >
              <option value="title" className="bg-gray-800">Sort by Title</option>
              <option value="year" className="bg-gray-800">Sort by Year</option>
              <option value="id" className="bg-gray-800">Sort by ID</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results Section */}
      {error && (
        <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4 text-red-200">
          {error}
        </div>
      )}

      {(loading || searchLoading) ? (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400"></div>
          <span className="ml-3 text-white">Loading movies...</span>
        </div>
      ) : (
        <div>
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-semibold text-white">
              {searchQuery ? `Search Results (${filteredMovies.length})` : `Featured Movies (${filteredMovies.length})`}
            </h3>
          </div>
          
          {filteredMovies.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🎬</div>
              <h3 className="text-xl font-semibold text-white mb-2">No movies found</h3>
              <p className="text-gray-300">Try adjusting your search terms</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
              {filteredMovies.map((movie) => (
                <MovieCard key={movie.id} movie={movie} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default HomePage;
