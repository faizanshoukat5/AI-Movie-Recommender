#!/usr/bin/env python3
"""
Robust WSGI configuration for PythonAnywhere deployment
With error handling and diagnostics
"""
import sys
import os
import traceback

# Add your project directory to Python path
path = '/home/fizu/AI-Movie-Recommender'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['PYTHONANYWHERE_ENV'] = 'true'
os.environ['TMDB_API_KEY'] = '89cf1a0e526c7c36bafe8d77248d276d'

# Try to import the main application with error handling
try:
    from app_pythonanywhere import application
    print("✅ Successfully imported app_pythonanywhere")
except Exception as e:
    print(f"❌ Failed to import app_pythonanywhere: {e}")
    print("📋 Full traceback:")
    traceback.print_exc()
    
    # Fallback to a simple Flask app
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return jsonify({
            "message": "AI Movie Recommendation Engine API - Fallback Mode",
            "status": "error",
            "error": str(e),
            "note": "Main application failed to load"
        })
    
    @app.route('/health')
    def health():
        return jsonify({
            "status": "error",
            "error": "Main application failed to load",
            "fallback": True
        })
    
    @app.route('/debug')
    def debug():
        return jsonify({
            "python_path": sys.path,
            "working_directory": os.getcwd(),
            "project_path": path,
            "error": str(e),
            "traceback": traceback.format_exc()
        })
    
    application = app

# This is what PythonAnywhere will use
if __name__ == "__main__":
    application.run()
