from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from services.recommendation_engine import RecommendationEngine
from services.ai_service import AIEnhancementService
from services.chatbot_service import ChatbotService
from services.movie_database_service import MovieDatabaseService
from services.firebase_service import FirebaseService
from models.movie import MovieResponse, RecommendationRequest, RecommendationResponse

# Initialize recommendation engine
recommendation_engine = RecommendationEngine()
firebase_service = None  # Initialize lazily to avoid blocking startup
is_model_ready = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    global firebase_service, is_model_ready
    
    print("Starting Movie Recommendation API...")
    
    # Initialize Firebase (non-blocking)
    try:
        firebase_service = FirebaseService()
        print("✓ Firebase service initialized")
    except Exception as e:
        print(f"✗ Firebase initialization failed: {e}")
        print("App will continue without Firebase features")
    
    # Start ML model training in background
    print("Loading movie data and training model in background...")
    try:
        recommendation_engine.load_data()
        print("✓ Movie data loaded")
        recommendation_engine.train_model()
        print("✓ ML model trained")
        is_model_ready = True
    except Exception as e:
        print(f"✗ Model training failed: {e}")
    
    print("✓ Application startup complete!")
    yield

app = FastAPI(
    title="The Last Critic API",
    description="The Last Critic: AI-powered movie recommendation system using content-based filtering",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "The Last Critic API is running - Your final word on what to watch"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/recommend", response_model=RecommendationResponse)
async def get_recommendation(request: RecommendationRequest):
    """
    Get movie recommendation based on user preferences
    """
    if not is_model_ready:
        raise HTTPException(status_code=503, detail="Model is still loading, please try again in a moment")
    try:
        recommendation = recommendation_engine.recommend(
            movie_title=request.movie_title,
            user_preferences=request.user_preferences,
            num_recommendations=request.num_recommendations
        )
        return recommendation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/movies", response_model=List[MovieResponse])
async def get_movies(
    limit: int = 100,
    search: Optional[str] = None
):
    """
    Get list of available movies
    """
    try:
        movies = recommendation_engine.get_movies(limit=limit, search=search)
        return movies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/movies/search-by-preferences", response_model=List[MovieResponse])
async def search_movies_by_preferences(preferences: dict):
    """
    Search movies based on user preferences (genres, rating, decade)
    """
    try:
        movies = recommendation_engine.search_by_preferences(
            favorite_genres=preferences.get('favorite_genres', []),
            min_rating=preferences.get('min_rating', 0),
            preferred_decade=preferences.get('preferred_decade', 2020),
            limit=preferences.get('limit', 20)
        )
        return movies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/movies/{movie_id}", response_model=MovieResponse)
async def get_movie(movie_id: int):
    """
    Get details of a specific movie
    """
    try:
        movie = recommendation_engine.get_movie_by_id(movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        return movie
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/latest-movies")
async def get_latest_movies(region: Optional[str] = None, page: int = 1):
    """
    Get latest movies from TMDB API
    """
    try:
        movie_db_service = MovieDatabaseService()
        movies = movie_db_service.get_latest_movies(region=region, page=page)
        return {"movies": movies, "total": len(movies)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-movie")
async def analyze_movie(request: dict):
    """
    Analyze movie reviews using local Ollama
    """
    try:
        movie_title = request.get("movie_title")
        movie_year = request.get("movie_year", "2024")
        
        if not movie_title:
            raise HTTPException(status_code=400, detail="Movie title is required")
        
        from services.ollama_service import OllamaService
        ollama_service = OllamaService()
        analysis = ollama_service.analyze_movie_reviews(movie_title, movie_year)
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_with_ai(message: dict):
    """
    Chat with AI about movie preferences using OpenRouter
    """
    try:
        chatbot_service = ChatbotService()
        if not chatbot_service.enabled:
            raise HTTPException(status_code=503, detail="Chatbot service not available")
        
        response = chatbot_service.chat_about_preferences(message.get("message", ""))
        return {"response": response}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-movies")
async def generate_movies(preferences: dict):
    """
    Generate new movie suggestions using OpenAI based on preferences
    """
    try:
        ai_service = AIEnhancementService()
        if not ai_service.enabled:
            raise HTTPException(status_code=503, detail="AI service not available")
        
        movies = ai_service.generate_movie_suggestions(
            user_preferences=preferences.get("user_preferences", {}),
            count=preferences.get("count", 10)
        )
        return {"movies": movies}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Firebase Authentication Endpoints
@app.post("/api/auth/user")
async def create_or_update_user(user_data: dict):
    """
    Create or update user in Firestore after Google Sign-in
    """
    if not firebase_service:
        raise HTTPException(status_code=503, detail="Firebase service not available")
    try:
        user_id = user_data.get("uid")
        email = user_data.get("email")
        display_name = user_data.get("displayName")
        photo_url = user_data.get("photoURL")
        
        if not user_id or not email:
            raise HTTPException(status_code=400, detail="User ID and email are required")
        
        result = firebase_service.create_user(user_id, email, display_name, photo_url)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/auth/user/{user_id}")
async def get_user(user_id: str):
    """
    Get user data from Firestore
    """
    if not firebase_service:
        raise HTTPException(status_code=503, detail="Firebase service not available")
    try:
        user = firebase_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/auth/user/{user_id}/preferences")
async def update_preferences(user_id: str, preferences: dict):
    """
    Update user preferences
    """
    if not firebase_service:
        raise HTTPException(status_code=503, detail="Firebase service not available")
    try:
        result = firebase_service.update_user_preferences(user_id, preferences)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/user/{user_id}/watch-history")
async def add_watch_history(user_id: str, movie_data: dict):
    """
    Add movie to user's watch history
    """
    if not firebase_service:
        raise HTTPException(status_code=503, detail="Firebase service not available")
    try:
        result = firebase_service.add_to_watch_history(user_id, movie_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/user/{user_id}/favorites/{movie_id}")
async def add_favorite(user_id: str, movie_id: str):
    """
    Add movie to user's favorites
    """
    if not firebase_service:
        raise HTTPException(status_code=503, detail="Firebase service not available")
    try:
        result = firebase_service.add_to_favorites(user_id, movie_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/auth/user/{user_id}/favorites/{movie_id}")
async def remove_favorite(user_id: str, movie_id: str):
    """
    Remove movie from user's favorites
    """
    if not firebase_service:
        raise HTTPException(status_code=503, detail="Firebase service not available")
    try:
        result = firebase_service.remove_from_favorites(user_id, movie_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/auth/user/{user_id}/favorites")
async def get_favorites(user_id: str):
    """
    Get user's favorite movies
    """
    if not firebase_service:
        raise HTTPException(status_code=503, detail="Firebase service not available")
    try:
        favorites = firebase_service.get_user_favorites(user_id)
        return {"favorites": favorites}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
