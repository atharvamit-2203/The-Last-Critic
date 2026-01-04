export interface Movie {
  id: number
  title: string
  genres: string
  description: string
  rating: number
  year: number
  release_month?: number
  reason?: string
  similarity_score?: number
  mass_rating?: number
  cinephile_rating?: number
  poster_url?: string
  backdrop_url?: string
  language?: string
  industry?: string
}

export interface UserPreferences {
  favorite_genres: string[]
  min_rating: number
  preferred_decade: number
}

export interface RecommendationRequest {
  movie_title: string
  user_preferences: UserPreferences
  num_recommendations: number
}

export interface RecommendationResponse {
  should_watch: boolean
  confidence: number
  reason: string
  recommended_movies: Movie[]
  target_movie: Movie | null
}
