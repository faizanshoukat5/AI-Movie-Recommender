#!/usr/bin/env python3
"""
Simple WSGI test file for PythonAnywhere
Use this to test basic Flask functionality
"""
import sys
import os

# Add your project directory to Python path
path = '/home/fizu/AI-Movie-Recommender'
if path not in sys.path:
    sys.path.insert(0, path)

# Simple Flask app for testing
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello! Basic Flask is working on PythonAnywhere!"

@app.route('/test')
def test():
    return {"status": "Flask routing is working", "path": path}

# This is what PythonAnywhere will use
application = app

if __name__ == "__main__":
    app.run(debug=True)
