#!/usr/bin/env python3
"""
Check dependencies for PythonAnywhere deployment
"""
import sys
import os

print("🔍 Dependency Check for PythonAnywhere")
print("=" * 50)

# Check Python version
print(f"Python version: {sys.version}")
print(f"Python path: {sys.executable}")

# Check required packages
required_packages = [
    'flask',
    'flask_cors',
    'pandas',
    'numpy',
    'sklearn',
    'requests',
    'firebase_admin'
]

print("\n📦 Package Check:")
for package in required_packages:
    try:
        __import__(package)
        print(f"✅ {package} - Available")
    except ImportError as e:
        print(f"❌ {package} - Missing: {e}")

# Check project files
print("\n📁 Project Files Check:")
project_files = [
    'app_pythonanywhere.py',
    'config_pythonanywhere.py',
    'production_rating_db.py',
    'tmdb_client.py',
    'wsgi.py'
]

for file in project_files:
    if os.path.exists(file):
        print(f"✅ {file} - Found")
    else:
        print(f"❌ {file} - Missing")

# Check if we can import our modules
print("\n🔧 Module Import Check:")
try:
    from config_pythonanywhere import PythonAnywhereConfig
    print("✅ config_pythonanywhere - OK")
except Exception as e:
    print(f"❌ config_pythonanywhere - Error: {e}")

try:
    from production_rating_db import ProductionRatingDatabase
    print("✅ production_rating_db - OK")
except Exception as e:
    print(f"❌ production_rating_db - Error: {e}")

try:
    from tmdb_client import TMDBClient
    print("✅ tmdb_client - OK")
except Exception as e:
    print(f"❌ tmdb_client - Error: {e}")

print("\n" + "=" * 50)
print("🎯 Run this script on PythonAnywhere to diagnose issues")
