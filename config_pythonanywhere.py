"""
PythonAnywhere-specific configuration for AI Movie Recommendation Engine
Optimized for PythonAnywhere hosting limitations and features
"""
import os
from datetime import timedelta

class PythonAnywhereConfig:
    """PythonAnywhere-specific configuration"""
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
    DEBUG = False
    TESTING = False
    
    # Database configuration - PythonAnywhere uses SQLite by default
    DATABASE_TYPE = 'sqlite'
    DATABASE_PATH = '/home/yourusername/mysite/ratings.db'  # Update with your username
    
    # MySQL configuration (for paid PythonAnywhere plans)
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'yourusername.mysql.pythonanywhere-services.com')
    MYSQL_USER = os.getenv('MYSQL_USER', 'yourusername')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'yourusername$movierecommendations')
    
    # Cache configuration - Simple in-memory cache for PythonAnywhere
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # TMDB API configuration
    TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')
    TMDB_BASE_URL = 'https://api.themoviedb.org/3'
    TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p'
    
    # Firebase configuration
    FIREBASE_SERVICE_ACCOUNT_PATH = '/home/yourusername/mysite/firebase-service-account.json'
    
    # Machine Learning configuration - Optimized for PythonAnywhere
    ML_MODEL_CACHE_TIMEOUT = 1800  # 30 minutes (shorter for memory constraints)
    ML_RECOMMENDATION_CACHE_TIMEOUT = 600  # 10 minutes
    
    # PythonAnywhere-specific settings
    MAX_CONTENT_LENGTH = 1048576  # 1MB (smaller for PythonAnywhere)
    PYTHONANYWHERE_DOMAIN = os.getenv('PYTHONANYWHERE_DOMAIN', 'yourusername.pythonanywhere.com')
    
    # CORS configuration for PythonAnywhere
    CORS_ORIGINS = [
        'https://ai-movie-recommendation-engine.web.app',
        'https://ai-movie-recommendation-engine.firebaseapp.com',
        'http://localhost:3000',
        'http://127.0.0.1:3000'
    ]
    
    # Logging configuration
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = '/home/yourusername/mysite/logs/app.log'
    
    # Performance settings for PythonAnywhere
    ENABLE_THREADING = True
    THREADED = True
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    @staticmethod
    def get_database_url():
        """Get database URL for PythonAnywhere"""
        if PythonAnywhereConfig.MYSQL_PASSWORD:
            return f"mysql://{PythonAnywhereConfig.MYSQL_USER}:{PythonAnywhereConfig.MYSQL_PASSWORD}@{PythonAnywhereConfig.MYSQL_HOST}/{PythonAnywhereConfig.MYSQL_DATABASE}"
        else:
            return f"sqlite:///{PythonAnywhereConfig.DATABASE_PATH}"
    
    @staticmethod
    def validate_pythonanywhere_setup():
        """Validate PythonAnywhere-specific setup"""
        errors = []
        warnings = []
        
        # Check required files
        required_files = [
            '/home/yourusername/mysite/app_pythonanywhere.py',
            '/home/yourusername/mysite/wsgi.py'
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                errors.append(f"Required file missing: {file_path}")
        
        # Check TMDB API key
        if not PythonAnywhereConfig.TMDB_API_KEY:
            warnings.append("TMDB_API_KEY not set - movie posters will not work")
        
        # Check Firebase config
        if not os.path.exists(PythonAnywhereConfig.FIREBASE_SERVICE_ACCOUNT_PATH):
            warnings.append("Firebase service account file not found - Firebase features will be disabled")
        
        return errors, warnings

class PythonAnywhereDevelopmentConfig(PythonAnywhereConfig):
    """Development configuration for PythonAnywhere"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    CACHE_DEFAULT_TIMEOUT = 60

# Configuration for PythonAnywhere
pythonanywhere_config = PythonAnywhereConfig
