#!/usr/bin/env python3
"""
Diagnostic script for PythonAnywhere deployment issues
Run this on PythonAnywhere to identify and fix import problems
"""
import sys
import os
import traceback

print("🔍 PythonAnywhere Deployment Diagnostics")
print("=" * 60)

# Add project path
project_path = '/home/fizu/AI-Movie-Recommender'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

print(f"📁 Project Path: {project_path}")
print(f"📂 Current Working Directory: {os.getcwd()}")
print(f"🐍 Python Version: {sys.version}")

# Check if we're in the right directory
print(f"\n📋 Directory Contents:")
try:
    files = os.listdir(project_path)
    for file in sorted(files):
        print(f"  - {file}")
except Exception as e:
    print(f"❌ Error listing directory: {e}")

# Check required files
print(f"\n📝 Required Files Check:")
required_files = [
    'app_pythonanywhere.py',
    'config_pythonanywhere.py',
    'production_rating_db.py',
    'tmdb_client.py',
    'wsgi.py',
    'requirements_production.txt'
]

for file in required_files:
    file_path = os.path.join(project_path, file)
    if os.path.exists(file_path):
        print(f"  ✅ {file}")
    else:
        print(f"  ❌ {file} - MISSING")

# Check Python packages
print(f"\n📦 Python Packages Check:")
packages = [
    'flask',
    'flask_cors',
    'pandas',
    'numpy',
    'sklearn',
    'requests',
    'firebase_admin'
]

for package in packages:
    try:
        __import__(package)
        print(f"  ✅ {package}")
    except ImportError as e:
        print(f"  ❌ {package} - {e}")

# Try to import configuration
print(f"\n🔧 Configuration Import Test:")
try:
    from config_pythonanywhere import PythonAnywhereConfig
    print("  ✅ config_pythonanywhere imported successfully")
except Exception as e:
    print(f"  ❌ config_pythonanywhere import failed: {e}")
    traceback.print_exc()

# Try to import database
print(f"\n🗄️ Database Import Test:")
try:
    from production_rating_db import ProductionRatingDatabase
    print("  ✅ production_rating_db imported successfully")
except Exception as e:
    print(f"  ❌ production_rating_db import failed: {e}")
    try:
        from rating_db import RatingDatabase
        print("  ✅ rating_db imported successfully (fallback)")
    except Exception as e2:
        print(f"  ❌ rating_db import also failed: {e2}")

# Try to import TMDB client
print(f"\n🎬 TMDB Client Import Test:")
try:
    from tmdb_client import TMDBClient
    print("  ✅ tmdb_client imported successfully")
except Exception as e:
    print(f"  ❌ tmdb_client import failed: {e}")

# Try to import the main app
print(f"\n🚀 Main Application Import Test:")
try:
    from app_pythonanywhere import application
    print("  ✅ app_pythonanywhere imported successfully")
    print(f"  ✅ Flask application object: {type(application)}")
except Exception as e:
    print(f"  ❌ app_pythonanywhere import failed: {e}")
    print(f"\n📋 Full traceback:")
    traceback.print_exc()

print(f"\n" + "=" * 60)
print("🎯 Diagnosis Complete!")
print("\nIf you see import errors above, run the following:")
print("1. pip3.10 install --user <missing_package>")
print("2. Check file permissions: chmod 755 *.py")
print("3. Ensure all files are in the correct location")
print("4. Reload your web app after fixing issues")
