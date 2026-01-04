import axios from 'axios'
import type { Movie, RecommendationRequest, RecommendationResponse } from '@/types'
import { requestCache } from '@/utils/requestCache'

const API_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8000')

const api = axios.create({
  baseURL: API_URL,
  timeout: 15000, // 15 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
})

export const getAllMovies = async (limit: number = 100, search?: string): Promise<Movie[]> => {
  const cacheKey = `all_movies_${limit}_${search || 'all'}`
  return requestCache.get(cacheKey, async () => {
    const params = new URLSearchParams()
    params.append('limit', limit.toString())
    if (search) params.append('search', search)
    
    const response = await api.get<Movie[]>(`/api/all-movies?${params.toString()}`)
    return response.data
  })
}

export const getMovies = async (limit: number = 100, search?: string): Promise<Movie[]> => {
  const cacheKey = `movies_${limit}_${search || 'all'}`
  return requestCache.get(cacheKey, async () => {
    const params = new URLSearchParams()
    params.append('limit', limit.toString())
    if (search) params.append('search', search)
    
    const response = await api.get<Movie[]>(`/api/movies?${params.toString()}`)
    return response.data
  })
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

export const waitForBackend = async (maxRetries: number = 30): Promise<boolean> => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      await checkHealth()
      return true
    } catch (error) {
      console.log(`Backend not ready, retrying... (${i + 1}/${maxRetries})`)
      await new Promise(resolve => setTimeout(resolve, 1000))
    }
  }
  return false
}

export const chatWithAI = async (message: string): Promise<{ response: string }> => {
  const response = await api.post('/api/chat', { message })
  return response.data
}

export const getLatestMovies = async (region?: string, page: number = 1): Promise<any> => {
  const cacheKey = `latest_${region || 'all'}_${page}`
  return requestCache.get(cacheKey, async () => {
    const params = new URLSearchParams()
    if (region) params.append('region', region)
    params.append('page', page.toString())
    params.append('limit', '100')  // Request 100 movies
    
    const response = await api.get(`/api/latest-movies?${params.toString()}`, {
      timeout: 10000  // Reduce timeout to 10 seconds
    })
    return response.data
  }, 300000) // Cache for 5 minutes instead of 10
}

export const analyzeMovie = async (data: { movie_title: string; movie_year: string }): Promise<any> => {
  const cacheKey = `analysis_${data.movie_title}_${data.movie_year}`
  return requestCache.get(cacheKey, async () => {
    const response = await api.post('/api/analyze-movie', data, {
      timeout: 90000
    })
    return response.data
  }, 1800000) // Cache for 30 minutes
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

// User recommendation functions
export const addRecommendation = async (userId: string, movieData: {
  movie_id: number
  movie_title: string
  movie_genres: string
  movie_rating: number
  movie_year: number
  movie_description: string
  source?: string
}): Promise<any> => {
  const response = await api.post(`/api/auth/user/${userId}/recommendations`, movieData)
  return response.data
}

export const getUserRecommendations = async (userId: string): Promise<any> => {
  const response = await api.get(`/api/auth/user/${userId}/recommendations`)
  return response.data
}
