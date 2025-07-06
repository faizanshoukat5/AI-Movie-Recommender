"""
Production configuration for AI Movie Recommendation Engine
"""
import os
from datetime import timedelta

class ProductionConfig:
    """Production configuration"""
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
    DEBUG = False
    TESTING = False
    
    # Database configuration
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')  # 'sqlite' or 'postgresql'
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///ratings.db')
    
    # PostgreSQL configuration (if using PostgreSQL)
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'movie_recommendations')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Redis configuration (for caching and background tasks)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Cache configuration
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')  # 'simple', 'redis', 'memcached'
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', '300'))  # 5 minutes
    
    # TMDB API configuration
    TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')
    TMDB_BASE_URL = 'https://api.themoviedb.org/3'
    TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p'
    
    # Firebase configuration
    FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH', 'firebase-service-account.json')
    
    # Machine Learning configuration
    ML_MODEL_CACHE_TIMEOUT = int(os.getenv('ML_MODEL_CACHE_TIMEOUT', '3600'))  # 1 hour
    ML_RECOMMENDATION_CACHE_TIMEOUT = int(os.getenv('ML_RECOMMENDATION_CACHE_TIMEOUT', '1800'))  # 30 minutes
    
    # API rate limiting
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '1000 per hour')
    
    # Security configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Performance configuration
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB
    
    # Background tasks configuration
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # Monitoring and health checks
    HEALTH_CHECK_ENABLED = os.getenv('HEALTH_CHECK_ENABLED', 'true').lower() == 'true'
    METRICS_ENABLED = os.getenv('METRICS_ENABLED', 'true').lower() == 'true'
    
    @staticmethod
    def get_database_config():
        """Get database configuration"""
        if ProductionConfig.DATABASE_TYPE.lower() == 'postgresql':
            return {
                'host': ProductionConfig.DB_HOST,
                'port': ProductionConfig.DB_PORT,
                'database': ProductionConfig.DB_NAME,
                'user': ProductionConfig.DB_USER,
                'password': ProductionConfig.DB_PASSWORD
            }
        else:
            return {
                'db_path': 'ratings.db'
            }
    
    @staticmethod
    def validate_config():
        """Validate configuration"""
        errors = []
        
        # Check required environment variables
        if not ProductionConfig.SECRET_KEY or ProductionConfig.SECRET_KEY == 'your-secret-key-change-this-in-production':
            errors.append("SECRET_KEY must be set to a secure random value")
        
        if not ProductionConfig.TMDB_API_KEY:
            errors.append("TMDB_API_KEY is required for movie poster functionality")
        
        if ProductionConfig.DATABASE_TYPE.lower() == 'postgresql':
            if not ProductionConfig.DB_PASSWORD:
                errors.append("DB_PASSWORD is required for PostgreSQL")
        
        if not os.path.exists(ProductionConfig.FIREBASE_SERVICE_ACCOUNT_PATH):
            errors.append(f"Firebase service account file not found: {ProductionConfig.FIREBASE_SERVICE_ACCOUNT_PATH}")
        
        return errors

class DevelopmentConfig(ProductionConfig):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'
    CACHE_DEFAULT_TIMEOUT = 60  # Shorter cache timeout for development

class TestingConfig(ProductionConfig):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'
    DATABASE_TYPE = 'sqlite'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
