from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class MovieResponse(BaseModel):
    id: int
    title: str
    genres: str
    description: str
    rating: float
    year: int
    release_month: Optional[int] = None
    reason: Optional[str] = None
    similarity_score: Optional[float] = None

class RecommendationRequest(BaseModel):
    movie_title: str = Field(..., description="Title of the movie to get recommendations for")
    user_preferences: Dict = Field(
        default={},
        description="User preferences including favorite_genres, min_rating, preferred_decade"
    )
    num_recommendations: int = Field(default=5, ge=1, le=20)

class RecommendationResponse(BaseModel):
    should_watch: bool
    confidence: float
    reason: str
    recommended_movies: List[MovieResponse]
    target_movie: Optional[MovieResponse]
