from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import json

app = FastAPI(title="The Last Critic API - Lightweight")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lightweight movie data
MOVIES = [
    {"id": 21, "title": "Avatar: Fire and Ash", "genres": "Action, Adventure, Sci-Fi", "description": "Jake Sully's family faces new threats on Pandora", "rating": 8.7, "year": 2025, "release_month": 12},
    {"id": 22, "title": "Dhurandhar", "genres": "Action, Drama, Thriller", "description": "Epic tale of courage and sacrifice in ancient India", "rating": 8.4, "year": 2025, "release_month": 12},
    {"id": 23, "title": "Thunderbolts", "genres": "Action, Adventure, Superhero", "description": "Marvel's anti-hero team assembles for their first mission", "rating": 7.9, "year": 2025, "release_month": 12},
    {"id": 26, "title": "Captain America: Brave New World", "genres": "Action, Adventure, Superhero", "description": "Sam Wilson faces new challenges as Captain America", "rating": 8.1, "year": 2026, "release_month": 1},
    {"id": 27, "title": "Lilo & Stitch", "genres": "Adventure, Comedy, Family", "description": "Live-action adaptation of the beloved Disney classic", "rating": 7.8, "year": 2026, "release_month": 1},
    {"id": 28, "title": "The Fantastic Four: First Steps", "genres": "Action, Adventure, Superhero", "description": "Marvel's first family begins their heroic journey", "rating": 8.3, "year": 2026, "release_month": 1},
]

class MovieResponse(BaseModel):
    id: int
    title: str
    genres: str
    description: str
    rating: float
    year: int
    release_month: Optional[int] = None

@app.get("/")
def read_root():
    return {"message": "The Last Critic API - Lightweight Version"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/movies", response_model=List[MovieResponse])
def get_movies(limit: int = 100, search: Optional[str] = None):
    movies = MOVIES
    if search:
        search_lower = search.lower()
        movies = [m for m in movies if search_lower in m["title"].lower() or search_lower in m["genres"].lower()]
    
    return movies[:limit]

@app.get("/api/all-movies", response_model=List[MovieResponse])
def get_all_movies(limit: int = 100, search: Optional[str] = None):
    return get_movies(limit, search)

@app.get("/api/latest-movies")
def get_latest_movies():
    return {"movies": [{"id": m["id"], "title": m["title"], "description": m["description"], "rating": m["rating"], "year": str(m["year"]), "genres": m["genres"], "industry": "International", "popularity": 9000} for m in MOVIES], "total": len(MOVIES)}

@app.post("/api/recommend")
def get_recommendation(request: dict):
    return {
        "should_watch": True,
        "confidence": 85.0,
        "reason": "Great movie based on your preferences!",
        "recommended_movies": MOVIES[:5],
        "target_movie": MOVIES[0] if MOVIES else None
    }

# Vercel handler
def handler(request, context):
    return app(request, context)