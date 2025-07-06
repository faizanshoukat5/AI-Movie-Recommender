import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../AuthContext';

const Navigation = ({ onAuthClick }) => {
  const location = useLocation();
  const { currentUser, userProfile, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const userMenuRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleLogout = async () => {
    try {
      await logout();
      setShowUserMenu(false);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const navItems = [
    { path: '/', label: 'Discover', icon: '🔍' },
    { path: '/recommendations', label: 'Recommendations', icon: '🎯' },
    { path: '/ratings', label: 'My Ratings', icon: '⭐' },
    { path: '/predict', label: 'Predict Rating', icon: '🔮' },
    { path: '/compare', label: 'Compare Models', icon: '📊' },
  ];

  // Add profile link if user is logged in
  if (currentUser) {
    navItems.push({ path: '/profile', label: 'Profile', icon: '👤' });
  }

  return (
    <nav className="bg-white/10 backdrop-blur-sm border-b border-white/20 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <span className="text-2xl">🎬</span>
            <span className="text-xl font-bold text-white">AI Movie Recommender</span>
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex space-x-1">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                  location.pathname === item.path
                    ? 'bg-purple-600 text-white shadow-lg'
                    : 'text-gray-300 hover:bg-white/10 hover:text-white'
                }`}
              >
                <span>{item.icon}</span>
                <span className="font-medium">{item.label}</span>
              </Link>
            ))}
          </div>

          {/* User Section */}
          <div className="flex items-center space-x-4">
            {currentUser ? (
              <div className="relative" ref={userMenuRef}>
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center space-x-3 hover:bg-white/10 rounded-lg p-2 transition-colors duration-200"
                >
                  <div className="text-right">
                    <div className="text-sm text-white font-medium">
                      {currentUser.displayName || userProfile?.displayName || 'Movie Enthusiast'}
                    </div>
                    <div className="text-xs text-gray-300">
                      {userProfile?.stats?.totalRatings || 0} ratings
                    </div>
                  </div>
                  {currentUser.photoURL || userProfile?.photoURL ? (
                    <img
                      src={currentUser.photoURL || userProfile.photoURL}
                      alt="Profile"
                      className="h-8 w-8 rounded-full border-2 border-white/30"
                    />
                  ) : (
                    <div className="h-8 w-8 rounded-full bg-purple-600 flex items-center justify-center text-white font-bold text-sm">
                      {(currentUser.displayName || userProfile?.displayName || 'U').charAt(0).toUpperCase()}
                    </div>
                  )}
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* User Dropdown Menu */}
                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-white/10 backdrop-blur-sm border border-white/20 rounded-lg shadow-lg z-50">
                    <div className="py-2">
                      <Link
                        to="/profile"
                        className="flex items-center px-4 py-2 text-sm text-white hover:bg-white/10 transition-colors duration-200"
                        onClick={() => setShowUserMenu(false)}
                      >
                        <span className="mr-3">👤</span>
                        View Profile
                      </Link>
                      <Link
                        to="/recommendations"
                        className="flex items-center px-4 py-2 text-sm text-white hover:bg-white/10 transition-colors duration-200"
                        onClick={() => setShowUserMenu(false)}
                      >
                        <span className="mr-3">🎯</span>
                        My Recommendations
                      </Link>
                      <Link
                        to="/ratings"
                        className="flex items-center px-4 py-2 text-sm text-white hover:bg-white/10 transition-colors duration-200"
                        onClick={() => setShowUserMenu(false)}
                      >
                        <span className="mr-3">⭐</span>
                        My Ratings
                      </Link>
                      <div className="border-t border-white/20 my-2"></div>
                      <button
                        onClick={handleLogout}
                        className="flex items-center w-full text-left px-4 py-2 text-sm text-red-300 hover:bg-red-500/20 transition-colors duration-200"
                      >
                        <span className="mr-3">🚪</span>
                        Sign Out
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <button
                onClick={onAuthClick}
                className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200"
              >
                Sign In
              </button>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button className="text-gray-300 hover:text-white p-2">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden pb-4">
          <div className="flex flex-wrap gap-2">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-1 px-3 py-2 rounded-lg text-sm transition-all duration-200 ${
                  location.pathname === item.path
                    ? 'bg-purple-600 text-white'
                    : 'text-gray-300 hover:bg-white/10 hover:text-white'
                }`}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            ))}
          </div>
          
          {/* Mobile User Section */}
          {!currentUser && (
            <div className="mt-4 pt-4 border-t border-white/20">
              <button
                onClick={onAuthClick}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200"
              >
                Sign In
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
