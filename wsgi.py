#!/usr/bin/env python3
"""
WSGI configuration for PythonAnywhere deployment
"""
import sys
import os

# Add your project directory to Python path
# Replace 'yourusername' with your actual PythonAnywhere username
path = '/home/yourusername/AI-Movie-Recommender'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['TMDB_API_KEY'] = '89cf1a0e526c7c36bafe8d77248d276d'

# Import Flask app
from app import app as application

if __name__ == "__main__":
    application.run()
