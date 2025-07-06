#!/usr/bin/env python3
"""
Fixed WSGI configuration for PythonAnywhere deployment
This will import and use the working application
"""
import sys
import os
import traceback

# Add your project directory to Python path (DIRECTORY, not file)
path = '/home/fizu/AI-Movie-Recommender'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['PYTHONANYWHERE_ENV'] = 'true'
os.environ['TMDB_API_KEY'] = '89cf1a0e526c7c36bafe8d77248d276d'

# Import the working application directly
try:
    # Import from the guaranteed working WSGI file
    sys.path.insert(0, '/home/fizu/AI-Movie-Recommender')
    from wsgi_working import application
    print("✅ Successfully imported working application")
except Exception as e:
    print(f"❌ Failed to import working application: {e}")
    print("📋 Full traceback:")
    traceback.print_exc()
    
    # Ultimate fallback - create minimal app
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return jsonify({
            "message": "AI Movie Recommendation Engine API - Emergency Fallback",
            "status": "error", 
            "error": str(e),
            "note": "Both main and working applications failed to load"
        })
    
    @app.route('/health')
    def health():
        return jsonify({
            "status": "error",
            "error": "All applications failed to load",
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
