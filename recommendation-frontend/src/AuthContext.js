import React, { createContext, useContext, useState, useEffect } from 'react';
import { 
  createUserWithEmailAndPassword, 
  signInWithEmailAndPassword, 
  signOut, 
  onAuthStateChanged,
  GoogleAuthProvider,
  signInWithPopup
} from 'firebase/auth';
import { doc, setDoc, getDoc } from 'firebase/firestore';
import { auth, db } from './firebaseConfig';

const AuthContext = createContext();

// Utility function to clean data for Firestore (removes undefined values)
const cleanDataForFirestore = (obj) => {
  if (obj === null || obj === undefined) {
    return null;
  }
  
  if (Array.isArray(obj)) {
    return obj.map(cleanDataForFirestore).filter(item => item !== undefined && item !== null);
  }
  
  if (typeof obj === 'object' && obj !== null) {
    const cleaned = {};
    for (const [key, value] of Object.entries(obj)) {
      if (value !== undefined) {
        const cleanedValue = cleanDataForFirestore(value);
        if (cleanedValue !== undefined) {
          cleaned[key] = cleanedValue;
        }
      }
    }
    return cleaned;
  }
  
  return obj;
};

export const useAuth = () => {
  return useContext(AuthContext);
};

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [userProfile, setUserProfile] = useState(null);

  // Sign up with email and password
  const signup = async (email, password, displayName) => {
    try {
      const result = await createUserWithEmailAndPassword(auth, email, password);
      
      // Create user profile in Firestore
      await setDoc(doc(db, 'users', result.user.uid), {
        email: result.user.email,
        displayName: displayName,
        createdAt: new Date().toISOString(),
        preferences: {
          favoriteGenres: [],
          watchlist: [],
          favorites: [],
          watched: [],
          ratings: {}
        },
        stats: {
          totalRatings: 0,
          totalMoviesWatched: 0,
          joinDate: new Date().toISOString()
        }
      });
      
      return result;
    } catch (error) {
      throw error;
    }
  };

  // Sign in with email and password
  const login = async (email, password) => {
    try {
      const result = await signInWithEmailAndPassword(auth, email, password);
      return result;
    } catch (error) {
      throw error;
    }
  };

  // Sign in with Google
  const loginWithGoogle = async () => {
    try {
      const provider = new GoogleAuthProvider();
      const result = await signInWithPopup(auth, provider);
      
      // Check if user profile exists, create if not
      const userDoc = await getDoc(doc(db, 'users', result.user.uid));
      if (!userDoc.exists()) {
        await setDoc(doc(db, 'users', result.user.uid), {
          email: result.user.email,
          displayName: result.user.displayName,
          photoURL: result.user.photoURL,
          createdAt: new Date().toISOString(),
          preferences: {
            favoriteGenres: [],
            watchlist: [],
            favorites: [],
            watched: [],
            ratings: {}
          },
          stats: {
            totalRatings: 0,
            totalMoviesWatched: 0,
            joinDate: new Date().toISOString()
          }
        });
      }
      
      return result;
    } catch (error) {
      throw error;
    }
  };

  // Sign out
  const logout = () => {
    return signOut(auth);
  };

  // Load user profile
  const loadUserProfile = async (userId) => {
    try {
      const userDoc = await getDoc(doc(db, 'users', userId));
      if (userDoc.exists()) {
        setUserProfile(userDoc.data());
      }
    } catch (error) {
      console.error('Error loading user profile:', error);
    }
  };

  // Update user preferences
  const updateUserPreferences = async (preferences) => {
    try {
      if (currentUser) {
        await setDoc(doc(db, 'users', currentUser.uid), {
          ...userProfile,
          preferences: { ...userProfile.preferences, ...preferences }
        }, { merge: true });
        
        setUserProfile(prev => ({
          ...prev,
          preferences: { ...prev.preferences, ...preferences }
        }));
      }
    } catch (error) {
      console.error('Error updating preferences:', error);
    }
  };

  // Add to watchlist
  const addToWatchlist = async (movieId, movieData) => {
    try {
      if (currentUser && userProfile) {
        const updatedWatchlist = [...userProfile.preferences.watchlist, { id: movieId, ...movieData, addedAt: new Date().toISOString() }];
        await updateUserPreferences({ watchlist: updatedWatchlist });
      }
    } catch (error) {
      console.error('Error adding to watchlist:', error);
    }
  };

  // Remove from watchlist
  const removeFromWatchlist = async (movieId) => {
    try {
      if (currentUser && userProfile) {
        const updatedWatchlist = userProfile.preferences.watchlist.filter(movie => movie.id !== movieId);
        await updateUserPreferences({ watchlist: updatedWatchlist });
      }
    } catch (error) {
      console.error('Error removing from watchlist:', error);
    }
  };

  // Add to favorites
  const addToFavorites = async (movieId, movieData) => {
    try {
      if (currentUser && userProfile) {
        const updatedFavorites = [...userProfile.preferences.favorites, { id: movieId, ...movieData, addedAt: new Date().toISOString() }];
        await updateUserPreferences({ favorites: updatedFavorites });
      }
    } catch (error) {
      console.error('Error adding to favorites:', error);
    }
  };

  // Get movie details for a rating
  const getMovieForRating = async (movieId) => {
    try {
      // First try to get from API
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/movies/${movieId}`);
      if (response.ok) {
        const movieData = await response.json();
        return {
          id: movieData.id || movieId,
          title: movieData.title || `Movie ${movieId}`,
          poster_url: movieData.poster_url || null
        };
      }
    } catch (error) {
      console.warn('Could not fetch movie details:', error);
    }
    
    // Return a basic movie object if API fails
    return {
      id: movieId,
      title: `Movie ${movieId}`,
      poster_url: null
    };
  };

  // Rate movie with enhanced data
  const rateMovie = async (movieId, rating, review = '') => {
    try {
      if (currentUser && userProfile) {
        // Get movie details for storage
        const movieDetails = await getMovieForRating(movieId);
        
        // Create clean rating object with no undefined values
        const ratingData = {
          rating: rating,
          review: review || '',
          ratedAt: new Date().toISOString(),
          movieTitle: movieDetails.title || `Movie ${movieId}`,
          moviePoster: movieDetails.poster_url || null
        };
        
        // Ensure all fields are defined and not undefined
        const cleanedRatingData = cleanDataForFirestore(ratingData);
        
        const updatedRatings = {
          ...userProfile.preferences.ratings,
          [movieId]: cleanedRatingData
        };
        
        const updatedStats = {
          ...userProfile.stats,
          totalRatings: Object.keys(updatedRatings).length
        };
        
        // Clean entire data structure before saving to Firestore
        const dataToSave = {
          preferences: { ...userProfile.preferences, ratings: updatedRatings },
          stats: updatedStats
        };
        
        const cleanedData = cleanDataForFirestore(dataToSave);
        
        // Update Firestore
        await setDoc(doc(db, 'users', currentUser.uid), cleanedData, { merge: true });
        
        // Update local state
        setUserProfile(prev => ({
          ...prev,
          preferences: { ...prev.preferences, ratings: updatedRatings },
          stats: updatedStats
        }));
        
        console.log('Movie rated and synced to Firestore');
      }
    } catch (error) {
      console.error('Error rating movie:', error);
      throw error;
    }
  };

  // Sync local ratings to Firebase when user logs in
  const syncLocalRatingsToFirebase = async (localRatings) => {
    try {
      if (currentUser && userProfile && localRatings && Object.keys(localRatings).length > 0) {
        console.log('Syncing local ratings to Firebase...');
        
        const updatedRatings = { ...userProfile.preferences.ratings };
        
        // Merge local ratings with existing Firebase ratings
        for (const [movieId, rating] of Object.entries(localRatings)) {
          if (!updatedRatings[movieId]) {
            // Get movie details for this rating
            try {
              const movieDetails = await getMovieForRating(movieId);
              
              // Create clean rating object with no undefined values
              const ratingData = {
                rating: rating,
                review: '',
                ratedAt: new Date().toISOString(),
                movieTitle: movieDetails.title || `Movie ${movieId}`,
                moviePoster: movieDetails.poster_url || null
              };
              
              // Clean the rating data to remove any undefined values
              updatedRatings[movieId] = cleanDataForFirestore(ratingData);
            } catch (error) {
              console.warn(`Could not sync rating for movie ${movieId}:`, error);
            }
          }
        }
        
        // Clean entire ratings object
        const cleanedRatings = cleanDataForFirestore(updatedRatings);
        
        const updatedStats = {
          ...userProfile.stats,
          totalRatings: Object.keys(cleanedRatings).length
        };
        
        // Prepare data for Firestore
        const dataToSave = {
          preferences: { ...userProfile.preferences, ratings: cleanedRatings },
          stats: updatedStats
        };
        
        // Clean the entire data structure
        const cleanedData = cleanDataForFirestore(dataToSave);
        
        // Update Firestore with synced ratings
        await setDoc(doc(db, 'users', currentUser.uid), cleanedData, { merge: true });
        
        // Update local state
        setUserProfile(prev => ({
          ...prev,
          preferences: { ...prev.preferences, ratings: cleanedRatings },
          stats: updatedStats
        }));
        
        console.log('Local ratings synced to Firebase successfully');
      }
    } catch (error) {
      console.error('Error syncing local ratings to Firebase:', error);
    }
  };

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setCurrentUser(user);
      if (user) {
        await loadUserProfile(user.uid);
        // Sync local ratings to Firebase
        const localRatings = JSON.parse(localStorage.getItem('movieRatings')) || {};
        await syncLocalRatingsToFirebase(localRatings);
      } else {
        setUserProfile(null);
      }
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  const value = {
    currentUser,
    userProfile,
    signup,
    login,
    loginWithGoogle,
    logout,
    updateUserPreferences,
    addToWatchlist,
    removeFromWatchlist,
    addToFavorites,
    rateMovie,
    syncLocalRatingsToFirebase,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
