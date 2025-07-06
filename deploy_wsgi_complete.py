#!/usr/bin/env python3
"""
COPY-PASTE DEPLOYMENT SCRIPT FOR PYTHONANYWHERE
Replace the content of /home/fizu/AI-Movie-Recommender/wsgi.py with this entire file
"""

# Copy the entire content below to PythonAnywhere wsgi.py file
print("🚀 Deploying complete WSGI file to PythonAnywhere...")

with open('wsgi_working.py', 'r') as f:
    content = f.read()

print("📋 Copy the following content to PythonAnywhere wsgi.py:")
print("=" * 80)
print(content)
print("=" * 80)

print("\n✅ Deployment Instructions:")
print("1. Go to PythonAnywhere Files tab")
print("2. Navigate to /home/fizu/AI-Movie-Recommender/")
print("3. Edit wsgi.py file")
print("4. Replace ALL content with the content above")
print("5. Save the file")
print("6. Go to Web tab and click 'Reload fizu.pythonanywhere.com'")
print("7. Test: https://fizu.pythonanywhere.com/models")
print("8. Frontend should now work without 'Error fetching models' error")
