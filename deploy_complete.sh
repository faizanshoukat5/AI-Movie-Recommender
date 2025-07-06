#!/bin/bash
# Complete PythonAnywhere deployment script
# Run this in your PythonAnywhere Bash Console

echo "🚀 Starting Complete PythonAnywhere Deployment"
echo "=" * 60

# Navigate to project directory
cd /home/fizu/AI-Movie-Recommender || {
    echo "❌ Project directory not found"
    exit 1
}

echo "📁 Current directory: $(pwd)"

# Pull latest code
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Install dependencies
echo "📦 Installing Python packages..."
pip3.10 install --user flask flask-cors pandas numpy scikit-learn requests firebase-admin

# Create directories
echo "📁 Creating required directories..."
mkdir -p logs
chmod 755 logs

# Fix permissions
echo "🔧 Setting file permissions..."
chmod 755 *.py

# Clean database
echo "🗄️ Setting up database..."
python3.10 cleanup_database.py

# Test imports
echo "🔍 Testing application imports..."
python3.10 -c "
try:
    from wsgi_working import application
    print('✅ Working app imported successfully')
    print(f'✅ App type: {type(application)}')
except Exception as e:
    print(f'❌ Import failed: {e}')
    exit(1)
"

# Test endpoints locally
echo "🔍 Testing endpoints..."
python3.10 -c "
from wsgi_working import application
with application.test_client() as client:
    response = client.get('/health')
    print(f'✅ Health endpoint: {response.status_code}')
    
    response = client.get('/status')
    print(f'✅ Status endpoint: {response.status_code}')
    
    response = client.get('/movies/search?q=action')
    print(f'✅ Search endpoint: {response.status_code}')
"

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Set WSGI file to: /home/fizu/AI-Movie-Recommender/wsgi_working.py" 
echo "3. Click 'Reload'"
echo "4. Test: https://fizu.pythonanywhere.com/health"
echo ""
echo "🎉 Your AI Movie Recommendation Engine is ready!"
