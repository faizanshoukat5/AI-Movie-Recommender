#!/bin/bash
# PythonAnywhere Deployment Script
# Run this in your PythonAnywhere bash console

echo "🐍 PythonAnywhere Deployment Starting..."

# Clone or update repository
if [ -d "AI-Movie-Recommender" ]; then
    echo "📁 Updating existing repository..."
    cd AI-Movie-Recommender
    git pull origin main
else
    echo "📁 Cloning repository..."
    git clone https://github.com/faizanshoukat5/AI-Movie-Recommender.git
    cd AI-Movie-Recommender
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3.10 install --user -r requirements.txt

# Set executable permissions
chmod +x *.sh

echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Go to Web tab in PythonAnywhere"
echo "2. Create new web app (Manual config, Python 3.10)"
echo "3. Update WSGI file with contents from wsgi.py"
echo "4. Replace 'yourusername' with your actual username"
echo "5. Reload web app"
echo ""
echo "Your backend will be available at: https://yourusername.pythonanywhere.com"
