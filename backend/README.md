# Movie Recommendation Backend

AI-powered movie recommendation system backend built with FastAPI and Python.

## Features

- **Content-Based Filtering**: Uses TF-IDF vectorization and cosine similarity
- **RESTful API**: FastAPI-based endpoints for recommendations
- **Machine Learning**: Scikit-learn for similarity calculations
- **Personalized Recommendations**: Analyzes user preferences (genres, ratings, years)

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
```

## Running the Server

```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check
```
GET /health
```

### Get Movies
```
GET /api/movies?limit=100&search=action
```

### Get Movie by ID
```
GET /api/movies/{movie_id}
```

### Get Recommendations
```
POST /api/recommend
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

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── models/                 # Pydantic models
│   ├── __init__.py
│   └── movie.py
├── services/              # Business logic
│   ├── __init__.py
│   └── recommendation_engine.py
├── data/                  # Movie datasets
│   └── movies.csv
└── requirements.txt       # Python dependencies
```

## Machine Learning Approach

1. **TF-IDF Vectorization**: Converts movie metadata (genres, descriptions) into numerical features
2. **Cosine Similarity**: Measures similarity between movies
3. **Preference Matching**: Analyzes user preferences against movie attributes
4. **Confidence Scoring**: Provides confidence level for recommendations

## API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
