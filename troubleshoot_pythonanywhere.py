#!/usr/bin/env python3
"""
Step-by-step troubleshooting for PythonAnywhere deployment
This will test each component individually
"""
import sys
import os
import traceback

print("🔍 Step-by-Step Troubleshooting")
print("=" * 60)

# Add project path
project_path = '/home/fizu/AI-Movie-Recommender'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

print(f"📁 Project Path: {project_path}")

# Step 1: Test basic imports
print("\n🔸 Step 1: Testing Basic Python Imports")
basic_imports = ['sys', 'os', 'json', 'time', 'datetime']
for module in basic_imports:
    try:
        __import__(module)
        print(f"  ✅ {module}")
    except ImportError as e:
        print(f"  ❌ {module}: {e}")

# Step 2: Test Flask and related imports
print("\n🔸 Step 2: Testing Flask Imports")
flask_imports = ['flask', 'flask_cors']
for module in flask_imports:
    try:
        __import__(module)
        print(f"  ✅ {module}")
    except ImportError as e:
        print(f"  ❌ {module}: {e}")

# Step 3: Test ML imports
print("\n🔸 Step 3: Testing ML Imports")
ml_imports = ['pandas', 'numpy', 'sklearn']
for module in ml_imports:
    try:
        __import__(module)
        print(f"  ✅ {module}")
    except ImportError as e:
        print(f"  ❌ {module}: {e}")

# Step 4: Test project-specific imports
print("\n🔸 Step 4: Testing Project-Specific Imports")
try:
    from config_pythonanywhere import PythonAnywhereConfig
    print("  ✅ config_pythonanywhere")
except Exception as e:
    print(f"  ❌ config_pythonanywhere: {e}")
    traceback.print_exc()

try:
    from tmdb_client import TMDBClient
    print("  ✅ tmdb_client")
except Exception as e:
    print(f"  ❌ tmdb_client: {e}")
    traceback.print_exc()

# Step 5: Test database imports with detailed error handling
print("\n🔸 Step 5: Testing Database Imports")
try:
    print("  🔍 Trying production_rating_db import...")
    from production_rating_db import get_production_rating_db
    print("  ✅ production_rating_db imported")
    
    print("  🔍 Trying to create database instance...")
    db = get_production_rating_db()
    print("  ✅ Database instance created")
    
    print("  🔍 Trying database initialization...")
    if hasattr(db, 'init_database'):
        result = db.init_database()
        print(f"  ✅ Database initialization: {result}")
    else:
        print("  ⚠️  No init_database method found")
        
except Exception as e:
    print(f"  ❌ production_rating_db: {e}")
    traceback.print_exc()

# Step 6: Test main app import with detailed error handling
print("\n🔸 Step 6: Testing Main App Import")
try:
    print("  🔍 Importing app_pythonanywhere...")
    import app_pythonanywhere
    print("  ✅ app_pythonanywhere module imported")
    
    print("  🔍 Accessing application object...")
    app = app_pythonanywhere.application
    print(f"  ✅ Application object: {type(app)}")
    
    print("  🔍 Testing app configuration...")
    print(f"  ✅ App name: {app.name}")
    print(f"  ✅ App config keys: {list(app.config.keys())}")
    
except Exception as e:
    print(f"  ❌ app_pythonanywhere: {e}")
    print("  📋 Full error details:")
    traceback.print_exc()

# Step 7: Test minimal Flask app
print("\n🔸 Step 7: Testing Minimal Flask App")
try:
    from flask import Flask
    test_app = Flask(__name__)
    
    @test_app.route('/')
    def test_route():
        return "Test route working"
    
    print("  ✅ Minimal Flask app created successfully")
    
except Exception as e:
    print(f"  ❌ Minimal Flask app failed: {e}")

print("\n" + "=" * 60)
print("🎯 Troubleshooting Complete!")
print("\nNext steps based on results:")
print("1. Fix any missing imports with: pip3.10 install --user <package>")
print("2. If database issues persist, run: python3.10 cleanup_database.py")
print("3. If main app still fails, use minimal app temporarily")
print("4. Check file permissions: chmod 755 *.py")
print("5. Share the output of this script for further help")
