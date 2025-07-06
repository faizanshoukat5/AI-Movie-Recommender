# 🎬 AI Movie Recommendation Engine

A production-ready web application that provides personalized movie recommendations using multiple machine learning algorithms, real-time user authentication, and modern web technologies.

## ✨ Features

### 🤖 **Advanced Recommendation System**
- **Multiple ML Models**: SVD, NMF, Content-based, and Ensemble algorithms
- **Personalized Recommendations**: Tailored suggestions based on user preferences
- **Real-time Learning**: System improves with each user rating

### 🔐 **User Authentication & Profiles**
- **Firebase Auth**: Google login and email/password authentication
- **User Profiles**: Personal dashboards with ratings history
- **Real-time Sync**: Data synchronized across all devices
- **Watchlist**: Save movies to watch later

### 🎭 **Rich Movie Database**
- **TMDB Integration**: High-quality movie posters and metadata
- **Search & Browse**: Find movies by title, genre, or year
- **Detailed Information**: Cast, crew, ratings, and reviews
- **Rating System**: 5-star rating with optional reviews

### 🚀 **Production-Ready Backend**
- **Optimized for PythonAnywhere**: Lightweight, fast, and reliable
- **Intelligent Caching**: Reduced API response times
- **Health Monitoring**: Status and health check endpoints
- **Error Handling**: Graceful fallbacks and comprehensive logging

## 🌐 Live Demo

- **Frontend**: [ai-movie-recommendation-engine.web.app](https://ai-movie-recommendation-engine.web.app)
- **Backend API**: [fizu.pythonanywhere.com](https://fizu.pythonanywhere.com)

## 🛠️ Tech Stack

### Frontend
- **React 18** with modern hooks and context
- **Firebase SDK** for authentication and real-time database
- **Responsive Design** for mobile and desktop
- **Material-UI inspired** components

### Backend
- **Flask** with production optimizations
- **scikit-learn** for machine learning models
- **SQLite/PostgreSQL** for data persistence
- **Firebase Admin SDK** for server-side integration
- **TMDB API** for movie metadata

### Deployment
- **Frontend**: Firebase Hosting
- **Backend**: PythonAnywhere
- **Database**: Firebase Firestore + SQLite
- **Version Control**: GitHub

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/faizanshoukat5/AI-Movie-Recommender.git
cd AI-Movie-Recommender
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements_production.txt

# Set environment variables
export TMDB_API_KEY=your_tmdb_api_key
export FLASK_ENV=development

# Run backend
python app_pythonanywhere.py
```

### 3. Frontend Setup
```bash
cd recommendation-frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 4. Configure APIs
- Get TMDB API key from [themoviedb.org](https://www.themoviedb.org/settings/api)
- Set up Firebase project at [console.firebase.google.com](https://console.firebase.google.com)
- Update configuration files with your credentials

## 📚 Documentation

- **[PythonAnywhere Deployment](PYTHONANYWHERE_DEPLOYMENT.md)** - Complete deployment guide
- **[Production Backend](README_Production.md)** - Backend documentation
- **[Backend Upgrade Summary](BACKEND_UPGRADE_SUMMARY.md)** - Recent improvements
- **[Firebase Setup](FIREBASE_COMPLETE.md)** - Firebase integration guide

## 🔧 API Endpoints

### Health & Status
- `GET /` - API information
- `GET /health` - Health check
- `GET /status` - System status

### Movies
- `GET /movies/search?q=query` - Search movies
- `GET /movies/random` - Browse random movies
- `GET /movies/{id}/enhanced` - Movie details
- `POST /movies/{id}/rate` - Rate a movie

### Recommendations
- `GET /recommendations/{user_id}` - Get personalized recommendations
- `GET /recommendations/{user_id}?model=ensemble` - Specify algorithm

### User Data
- `GET /users/{user_id}/ratings` - User's ratings
- `GET /users/{user_id}/watchlist` - User's watchlist

## 🌟 Key Features

### For Users
- **Personalized Recommendations**: Get movies tailored to your taste
- **Rich Movie Database**: Discover new movies with detailed information
- **Cross-Device Sync**: Access your data from anywhere
- **Social Features**: Rate and review movies

### For Developers
- **Production-Ready**: Optimized for real-world deployment
- **Comprehensive Documentation**: Easy to understand and extend
- **Modern Architecture**: Clean, maintainable codebase
- **Scalable Design**: Ready for growth and new features

## 📊 Performance

- **API Response Time**: <500ms for cached responses
- **Recommendation Generation**: <2 seconds for complex algorithms
- **Frontend Loading**: <3 seconds initial load
- **Real-time Sync**: Instant updates across devices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [The Movie Database (TMDB)](https://www.themoviedb.org/) for movie data
- [MovieLens](https://grouplens.org/datasets/movielens/) for ratings dataset
- [Firebase](https://firebase.google.com/) for real-time features
- [PythonAnywhere](https://www.pythonanywhere.com/) for hosting

## 📞 Support

For support and questions:
- 📧 Email: [your-email@example.com]
- 🐛 Issues: [GitHub Issues](https://github.com/faizanshoukat5/AI-Movie-Recommender/issues)
- 📖 Documentation: Check the docs folder

---

**⭐ Star this repository if you found it helpful!**
