#!/usr/bin/env python3
"""
WSGI configuration for PythonAnywhere deployment
Updated for production-ready backend
"""
import sys
import os

# Add your project directory to Python path
# Replace 'yourusername' with your actual PythonAnywhere username
path = '/home/yourusername/mysite'  # Update this path
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['PYTHONANYWHERE_ENV'] = 'true'
os.environ['TMDB_API_KEY'] = '89cf1a0e526c7c36bafe8d77248d276d'

# Import the PythonAnywhere-optimized Flask app
from app_pythonanywhere import application

# This is what PythonAnywhere will use
if __name__ == "__main__":
    application.run()
