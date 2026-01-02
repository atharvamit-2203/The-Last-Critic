import axios from 'axios'
import type { Movie, RecommendationRequest, RecommendationResponse } from '@/types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  timeout: 15000, // 15 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
})

export const getMovies = async (limit: number = 100, search?: string): Promise<Movie[]> => {
  const params = new URLSearchParams()
  params.append('limit', limit.toString())
  if (search) params.append('search', search)
  
  const response = await api.get<Movie[]>(`/api/movies?${params.toString()}`)
  return response.data
}

export const getMovieById = async (id: number): Promise<Movie> => {
  const response = await api.get<Movie>(`/api/movies/${id}`)
  return response.data
}

export const getRecommendations = async (
  request: RecommendationRequest
): Promise<RecommendationResponse> => {
  const response = await api.post<RecommendationResponse>('/api/recommend', request)
  return response.data
}

export const checkHealth = async (): Promise<{ status: string }> => {
  const response = await api.get('/health')
  return response.data
}

export const chatWithAI = async (message: string): Promise<{ response: string }> => {
  const response = await api.post('/api/chat', { message })
  return response.data
}

export const getLatestMovies = async (region?: string, page: number = 1): Promise<any> => {
  const params = new URLSearchParams()
  if (region) params.append('region', region)
  params.append('page', page.toString())
  
  const response = await api.get(`/api/latest-movies?${params.toString()}`, {
    timeout: 30000 // 30 second timeout for TMDB
  })
  return response.data
}

export const analyzeMovie = async (data: { movie_title: string; movie_year: string }): Promise<any> => {
  const response = await api.post('/api/analyze-movie', data, {
    timeout: 60000 // 60 seconds for fast analysis
  })
  return response.data
}

export const searchMoviesByPreferences = async (preferences: {
  favorite_genres: string[]
  min_rating: number
  preferred_decade: number
  limit?: number
}): Promise<Movie[]> => {
  const response = await api.post<Movie[]>('/api/movies/search-by-preferences', preferences)
  return response.data
}
