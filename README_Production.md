# AI Movie Recommendation Engine - Production Backend

A production-ready Flask backend for the AI Movie Recommendation Engine with Firebase integration, advanced caching, and multiple machine learning models.

## 🚀 Features

### Core Features
- **Advanced Machine Learning**: Multiple recommendation algorithms (SVD, NMF, Content-based, Ensemble)
- **Firebase Integration**: Real-time synchronization with Firebase Firestore
- **Performance Optimization**: Intelligent caching and optimized database queries
- **Production-Ready**: Gunicorn WSGI server, PostgreSQL support, comprehensive logging
- **Movie Metadata**: TMDB API integration for movie posters, details, and trailers
- **User Management**: Rating system, watchlists, and user profiles

### Technical Stack
- **Backend**: Flask 2.3.3 with Flask-CORS
- **Database**: SQLite (development) / PostgreSQL (production)
- **Cache**: Redis (optional)
- **ML Libraries**: scikit-learn, pandas, numpy
- **Authentication**: Firebase Auth integration
- **API**: RESTful API with comprehensive endpoints

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+ (for frontend)
- Redis (optional, for caching)
- PostgreSQL (optional, for production)

## 🛠️ Installation

### Quick Start (Development)

```bash
# Clone the repository
git clone <repository-url>
cd AI-Recommendation-Engine

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements_production.txt

# Set environment variables
export TMDB_API_KEY=your_tmdb_api_key
export FLASK_ENV=development

# Run development server
python app_production.py
```

### Production Deployment

```bash
# Use the deployment script
chmod +x deploy_production.sh
./deploy_production.sh

# Or on Windows:
deploy_production.bat
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/production) | `development` |
| `PORT` | Server port | `5000` |
| `SECRET_KEY` | Flask secret key | (required for production) |
| `TMDB_API_KEY` | The Movie Database API key | (required) |
| `DATABASE_TYPE` | Database type (sqlite/postgresql) | `sqlite` |
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_NAME` | PostgreSQL database name | `movie_recommendations` |
| `DB_USER` | PostgreSQL username | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | (required for PostgreSQL) |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |

### Firebase Configuration

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Generate a service account key
3. Save it as `firebase-service-account.json` in the project root

### TMDB API Configuration

1. Sign up at [The Movie Database](https://www.themoviedb.org/)
2. Get your API key from the API settings
3. Set the `TMDB_API_KEY` environment variable

## 🔌 API Endpoints

### Health & Status
- `GET /` - API information
- `GET /health` - Health check
- `GET /status` - Detailed system status

### Movies
- `GET /movies/search?q=query` - Search movies
- `GET /movies/random?limit=20` - Get random movies
- `GET /movies/{id}/enhanced` - Get enhanced movie details
- `POST /movies/{id}/rate` - Rate a movie

### Recommendations
- `GET /recommendations/{user_id}` - Get user recommendations
- `GET /recommendations/{user_id}?model=svd` - Get recommendations from specific model

### User Data
- `GET /users/{user_id}/ratings` - Get user ratings
- `GET /users/{user_id}/watchlist` - Get user watchlist
- `POST /users/{user_id}/watchlist/{movie_id}` - Add to watchlist
- `DELETE /users/{user_id}/watchlist/{movie_id}` - Remove from watchlist

## 🤖 Machine Learning Models

### Available Models
1. **SVD (Singular Value Decomposition)** - Fast matrix factorization
2. **NMF (Non-negative Matrix Factorization)** - Interpretable recommendations
3. **Content-Based** - Genre and metadata similarity
4. **Ensemble** - Combination of multiple models

### Model Selection
- **Development**: Use `svd` for fastest results
- **Production**: Use `ensemble` for best accuracy
- **Cold Start**: Use `content` for new users

## 📊 Performance Optimization

### Caching Strategy
- **Recommendation Cache**: 5-minute cache for user recommendations
- **Movie Metadata Cache**: 30-minute cache for movie details
- **Search Cache**: 5-minute cache for search results

### Database Optimization
- **Indexes**: Optimized database indexes for fast queries
- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Minimized database queries

## 🔒 Security

### Authentication
- Firebase Auth integration for secure user authentication
- JWT token validation for protected endpoints
- CORS configuration for frontend integration

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- Rate limiting (configurable)

## 📈 Monitoring

### Health Checks
- `/health` endpoint for load balancer health checks
- Database connectivity monitoring
- Firebase integration status

### Logging
- Structured logging with configurable levels
- Access logs and error logs
- Performance metrics tracking

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest test_production.py -v

# Run with coverage
pytest test_production.py --cov=app_production --cov-report=html
```

### Test Coverage
- API endpoint testing
- Database operations testing
- Configuration validation
- Error handling testing

## 🚀 Deployment Options

### 1. Local Development
```bash
python app_production.py
```

### 2. Production with Gunicorn
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 app_production:app
```

### 3. Docker Deployment
```bash
# Build image
docker build -t movie-recommender .

# Run container
docker run -p 5000:5000 movie-recommender
```

### 4. Cloud Deployment
- **PythonAnywhere**: Upload files and configure WSGI
- **Heroku**: Use Procfile for deployment
- **AWS EC2**: Use deployment script
- **Google Cloud Run**: Container-based deployment

## 📁 Project Structure

```
AI-Recommendation-Engine/
├── app_production.py           # Production Flask application
├── production_rating_db.py     # Enhanced database module
├── config.py                   # Configuration management
├── requirements_production.txt # Production dependencies
├── deploy_production.sh        # Deployment script (Linux/Mac)
├── deploy_production.bat       # Deployment script (Windows)
├── test_production.py          # Comprehensive test suite
├── firebase-service-account.json # Firebase credentials
├── ml-100k/                    # MovieLens dataset
├── logs/                       # Log files
└── venv/                       # Virtual environment
```

## 🔧 Troubleshooting

### Common Issues

1. **TMDB API Key Not Working**
   - Verify API key is correct
   - Check API key permissions
   - Ensure API key is set in environment variables

2. **Firebase Integration Issues**
   - Check service account key file exists
   - Verify Firebase project configuration
   - Ensure proper IAM permissions

3. **Database Connection Issues**
   - Check PostgreSQL credentials
   - Verify database server is running
   - Check network connectivity

4. **Performance Issues**
   - Enable Redis caching
   - Optimize database queries
   - Consider using PostgreSQL for production

### Debug Mode
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app_production.py
```

## 📚 API Documentation

### Rate a Movie
```bash
POST /movies/1/rate
Content-Type: application/json

{
  "user_id": "user123",
  "rating": 4.5,
  "review": "Great movie!"
}
```

### Get Recommendations
```bash
GET /recommendations/123?model=ensemble&n=10
```

### Search Movies
```bash
GET /movies/search?q=inception&limit=10&include_posters=true
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [The Movie Database (TMDB)](https://www.themoviedb.org/) for movie data
- [MovieLens](https://grouplens.org/datasets/movielens/) for ratings dataset
- [Firebase](https://firebase.google.com/) for real-time database
- [Flask](https://flask.palletsprojects.com/) for web framework
- [scikit-learn](https://scikit-learn.org/) for machine learning

---

## 📞 Support

For support, please open an issue in the GitHub repository or contact the development team.

**Production Backend Version: 2.0**
**Last Updated: December 2024**
