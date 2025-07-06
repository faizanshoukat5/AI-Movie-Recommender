#!/bin/bash
# Frontend Update and Deployment Script

echo "🚀 Frontend Deployment Script"
echo "Current directory: $(pwd)"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Are you in the recommendation-frontend directory?"
    echo "Please run: cd recommendation-frontend"
    exit 1
fi

# Prompt for backend URL
echo ""
echo "📍 Enter your backend URL (e.g., https://yourusername.pythonanywhere.com):"
read -p "Backend URL: " BACKEND_URL

if [ -z "$BACKEND_URL" ]; then
    echo "❌ Error: Backend URL is required"
    exit 1
fi

# Update production environment file
echo "🔧 Updating production environment..."
echo "REACT_APP_API_URL=$BACKEND_URL" > .env.production

# Build the project
echo "🏗️ Building React app..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    
    # Deploy to Firebase
    echo "🚀 Deploying to Firebase Hosting..."
    firebase deploy --only hosting
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 Deployment Complete!"
        echo "📱 Frontend: https://ai-movie-recommendation-engine.web.app"
        echo "🖥️  Backend: $BACKEND_URL"
        echo ""
        echo "✅ Your AI Movie Recommendation Engine is now live!"
    else
        echo "❌ Firebase deployment failed"
        exit 1
    fi
else
    echo "❌ Build failed"
    exit 1
fi
