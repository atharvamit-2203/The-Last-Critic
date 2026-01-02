# The Last Critic - AI-Powered Movie Recommendation System

Your final word on what to watch. A full-stack AI/ML-based movie recommendation system that intelligently suggests whether users should watch particular movies based on their preferences.

## 🎯 Overview

**The Last Critic** combines machine learning with modern web technologies to deliver personalized movie recommendations. The system uses **content-based filtering** with **TF-IDF vectorization** and **cosine similarity** to analyze movie metadata and match it with user preferences.

*"When you can't decide what to watch, let The Last Critic have the final say."*

## 🏗️ Architecture

```
Movie-Recommendation/
├── backend/          # Python FastAPI + ML Engine
└── frontend/         # Next.js React Application
```

### Backend (Python/FastAPI)
- **Framework**: FastAPI for high-performance API
- **ML Libraries**: Scikit-learn for TF-IDF and cosine similarity
- **Data Processing**: Pandas for movie data management
- **Features**:
  - Content-based recommendation engine
  - TF-IDF vectorization of movie metadata
  - Cosine similarity calculations
  - Preference-based confidence scoring

### Frontend (Next.js/React)
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript for type safety
- **Styling**: Tailwind CSS for modern UI
- **Features**:
  - Interactive movie search
  - User preference configuration
  - Real-time recommendations
  - Confidence score visualization
  - Similar movie suggestions

## 🚀 Quick Start

### Windows Users (Recommended)

1. **One-Click Startup**:
   ```bash
   # Double-click the startup script
   start-the-last-critic.bat
   ```
   This will automatically:
   - Install Python dependencies
   - Install Node.js dependencies  
   - Start both backend and frontend
   - Open the application in your browser

2. **Access The Last Critic**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Setup

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the server:
```bash
python main.py
```

Backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

Frontend will run on `http://localhost:3000`

## 📊 How It Works

### 1. Content-Based Filtering
The system analyzes movie metadata including:
- **Genres** (Action, Drama, Sci-Fi, etc.)
- **Descriptions** (Plot summaries)
- **Titles** (Movie names)
- **Ratings** (User/critic scores)
- **Release Year**

### 2. TF-IDF Vectorization
Text features are converted into numerical vectors using Term Frequency-Inverse Document Frequency (TF-IDF), which:
- Identifies important terms in movie descriptions
- Reduces the weight of common words
- Creates a feature matrix for similarity comparison

### 3. Cosine Similarity
Measures similarity between movies by calculating the cosine of the angle between their feature vectors:
- Values range from 0 (completely different) to 1 (identical)
- Finds movies with similar content characteristics

### 4. Preference Matching
User preferences are analyzed against movie attributes:
- **Genre Matching**: Compares favorite genres with movie genres
- **Rating Threshold**: Filters by minimum acceptable rating
- **Decade Preference**: Considers release year preferences
- **Confidence Score**: Calculates match percentage (0-100%)

### 5. Recommendation Decision
- **Should Watch**: Confidence ≥ 60%
- **Maybe Skip**: Confidence < 60%
- Includes detailed reasoning for each recommendation
- Suggests similar movies based on content similarity

## 🎨 Features

### User Interface
- 🔍 **Smart Search**: Autocomplete movie search with real-time filtering
- 🎯 **Preference Panel**: 
  - Multi-select genre preferences
  - Adjustable rating slider
  - Decade selector
- 📊 **Recommendation Display**:
  - Clear yes/no decision
  - Confidence percentage
  - Detailed reasoning
  - Movie metadata (genres, rating, year, description)
- 🎬 **Similar Movies**: 5 content-based recommendations

### API Endpoints

#### GET `/api/movies`
Fetch available movies with optional search and limit
```json
{
  "limit": 100,
  "search": "action"
}
```

#### POST `/api/recommend`
Get personalized recommendation
```json
{
  "movie_title": "The Matrix",
  "user_preferences": {
    "favorite_genres": ["Action", "Sci-Fi"],
    "min_rating": 8.0,
    "preferred_decade": 1990
  },
  "num_recommendations": 5
}
```

#### GET `/api/movies/{id}`
Get specific movie details

#### GET `/health`
Health check endpoint

## 📁 Project Structure

### Backend
```
backend/
├── main.py                         # FastAPI application
├── models/
│   ├── movie.py                    # Pydantic models
│   └── __init__.py
├── services/
│   ├── recommendation_engine.py    # ML recommendation logic
│   └── __init__.py
├── data/
│   ├── movies.csv                  # Movie dataset
│   └── .gitkeep
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
└── README.md
```

### Frontend
```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx               # Main page
│   │   ├── layout.tsx             # Root layout
│   │   └── globals.css            # Global styles
│   ├── components/
│   │   ├── Header.tsx             # App header
│   │   ├── MovieSearch.tsx        # Search component
│   │   ├── PreferencesForm.tsx    # Preferences panel
│   │   ├── RecommendationResult.tsx # Results display
│   │   └── MovieCard.tsx          # Movie card component
│   ├── services/
│   │   └── api.ts                 # API integration
│   └── types/
│       └── index.ts               # TypeScript types
├── public/                        # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

## 🔧 Configuration

### Backend Environment Variables
```env
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000
DATA_PATH=data/movies.csv
```

### Frontend Environment Variables
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🧪 Machine Learning Details

### Training Process
1. Load movie dataset (CSV format)
2. Combine features: genres + description + title
3. Create TF-IDF matrix with:
   - Stop words removal
   - Bigram support (1-2 word phrases)
   - Maximum 5000 features
4. Calculate cosine similarity matrix
5. Store for real-time recommendations

### Recommendation Algorithm
```python
1. Find target movie in database
2. Get similarity scores with all other movies
3. Sort by similarity (descending)
4. Return top N similar movies
5. Analyze user preferences:
   - Genre overlap score (40%)
   - Rating threshold score (30%)
   - Decade preference score (30%)
6. Calculate confidence percentage
7. Determine should_watch (≥60% confidence)
```

## 🎯 Use Cases

1. **Movie Selection**: Help users decide if they should watch a specific movie
2. **Discovery**: Find similar movies based on content
3. **Preference Learning**: Understand viewing patterns and preferences
4. **Recommendation Engine**: Power movie streaming platforms
5. **Content Analysis**: Analyze movie similarities and patterns

## 🚀 Future Enhancements

- [ ] Collaborative filtering (user-based recommendations)
- [ ] Hybrid recommendation system
- [ ] User accounts and watch history
- [ ] Movie ratings and reviews
- [ ] Integration with TMDB/IMDB APIs
- [ ] Advanced filters (actors, directors, languages)
- [ ] Recommendation explanations with visualizations
- [ ] A/B testing for recommendation algorithms
- [ ] Mobile application

## 📚 Technologies Used

### Backend
- FastAPI - Modern Python web framework
- Scikit-learn - Machine learning library
- Pandas - Data manipulation
- NumPy - Numerical computing
- Pydantic - Data validation
- Uvicorn - ASGI server

### Frontend
- Next.js - React framework
- TypeScript - Type-safe JavaScript
- Tailwind CSS - Utility-first CSS
- Axios - HTTP client
- Lucide React - Icon library

## 📖 API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👥 Authors

AI-Powered Movie Recommendation System

## 🙏 Acknowledgments

- Scikit-learn for ML algorithms
- FastAPI for excellent API framework
- Next.js for modern React development
- The open-source community

---

**Note**: This is a demonstration project. For production use, consider:
- Larger movie datasets (TMDB, IMDB)
- Database integration (PostgreSQL, MongoDB)
- Caching layer (Redis)
- Authentication and authorization
- Rate limiting
- Comprehensive error handling
- Monitoring and logging
- Scalability considerations
