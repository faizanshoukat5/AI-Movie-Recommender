# 🎬 AI Movie Recommendation Engine - Original Version

A simple movie recommendation system built with Python Flask and React that provides personalized movie recommendations using SVD (Singular Value Decomposition) algorithm.

## 🚀 Features

- **Movie Recommendations**: Get personalized movie recommendations for any user
- **Rating Prediction**: Predict how a user would rate a specific movie
- **Movie Browser**: Browse through the complete movie catalog
- **Simple Interface**: Clean, easy-to-use web interface
- **Real Movie Data**: Uses the MovieLens 100k dataset with real movie titles

## 🛠️ Technology Stack

### Backend
- **Python 3.x**
- **Flask** - Web framework
- **Flask-CORS** - Cross-origin resource sharing
- **scikit-learn** - Machine learning (SVD algorithm)
- **pandas** - Data manipulation
- **numpy** - Numerical computing

### Frontend
- **React** - User interface
- **CSS3** - Styling with gradients and modern effects
- **JavaScript** - Interactive functionality

## 📦 Installation

### Prerequisites
- Python 3.x
- Node.js and npm
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "AI Recommendation Engine"
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the Flask server
python app.py
```

The backend will start on `http://localhost:5000`

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd recommendation-frontend

# Install dependencies
npm install

# Start the React development server
npm start
```

The frontend will start on `http://localhost:3000`

## 🎯 Usage

### 1. Get Recommendations
- Enter a User ID (1-943)
- Choose number of recommendations (1-50)
- Click "Get Recommendations"

### 2. Predict Rating
- Enter a User ID (1-943)
- Enter a Movie ID (1-1682)
- Click "Predict Rating"

### 3. Browse Movies
- View all movies in the dataset
- See movie IDs and titles

## 📊 Dataset

This application uses the MovieLens 100k dataset, which contains:
- 100,000 ratings from 943 users on 1,682 movies
- Ratings on a scale of 1-5
- Real movie titles and information

## 🔧 API Endpoints

- `GET /` - API status
- `GET /recommendations/<user_id>?n=<number>` - Get recommendations
- `GET /predict?user_id=<id>&item_id=<id>` - Predict rating
- `GET /movies` - Get all movies
- `GET /status` - System status

## 🎨 Features

- **Responsive Design**: Works on desktop and mobile
- **Modern UI**: Glassmorphism effects and smooth animations
- **Real-time Updates**: Instant results and feedback
- **Error Handling**: Graceful error messages
- **Loading States**: Visual feedback during processing

## 🔍 How It Works

1. **Data Loading**: Loads MovieLens 100k dataset
2. **Model Training**: Uses SVD algorithm to find latent factors
3. **Recommendations**: Predicts ratings for unseen movies
4. **Ranking**: Returns top-N highest predicted ratings

## 🚀 Quick Start

1. Run the switch script: `switch_to_original.bat`
2. Install dependencies: `pip install -r requirements.txt`
3. Start backend: `python app.py`
4. Start frontend: `cd recommendation-frontend && npm start`
5. Open `http://localhost:3000`

## 📝 Notes

- This is the original, simple version without authentication
- No user accounts or personalization beyond user ID
- Uses in-memory storage (no database)
- Designed for demonstration and learning purposes

## 🎯 Example Usage

**Get recommendations for user 1:**
```
GET /recommendations/1?n=10
```

**Predict rating for user 1, movie 50:**
```
GET /predict?user_id=1&item_id=50
```

Enjoy discovering new movies! 🍿
