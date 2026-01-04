'use client'

import React from 'react'
import { Star, TrendingUp, Heart } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { addRecommendation } from '@/services/api'

interface Movie {
  id: number
  title: string
  description: string
  rating: number
  year: string
  genres: string
  industry: string
  poster_url?: string
  popularity?: number
}

interface MovieGridProps {
  movies: Movie[]
  onMovieClick: (movie: Movie) => void
}

export default function MovieGrid({ movies, onMovieClick }: MovieGridProps) {
  const { user } = useAuth()

  const handleRecommend = async (e: React.MouseEvent, movie: Movie) => {
    e.stopPropagation()
    
    if (!user) return
    
    // Check if already recommended
    const recommendedMovies = JSON.parse(localStorage.getItem(`recommended_${user.uid}`) || '[]')
    if (recommendedMovies.includes(movie.id)) {
      return // Already recommended
    }
    
    try {
      await addRecommendation(user.uid, {
        movie_id: movie.id,
        movie_title: movie.title,
        movie_genres: movie.genres,
        movie_rating: movie.rating,
        movie_year: parseInt(movie.year),
        movie_description: movie.description,
        source: 'latest_movies'
      })
      
      // Store in localStorage for persistence
      recommendedMovies.push(movie.id)
      localStorage.setItem(`recommended_${user.uid}`, JSON.stringify(recommendedMovies))
      
      // Force re-render by updating state
      window.location.reload()
    } catch (error) {
      console.error('Error adding recommendation:', error)
    }
  }

  const isRecommended = (movieId: number) => {
    if (!user) return false
    const recommendedMovies = JSON.parse(localStorage.getItem(`recommended_${user.uid}`) || '[]')
    return recommendedMovies.includes(movieId)
  }

  if (movies.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        No movies available
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
      {movies.map((movie) => (
        <div
          key={movie.id}
          className="group relative bg-gray-800/50 rounded-xl overflow-hidden hover:ring-2 hover:ring-blue-500 transition-all hover:scale-105"
        >
          <button
            onClick={() => onMovieClick(movie)}
            className="w-full h-full cursor-pointer"
          >
            {/* Poster */}
            <div className="aspect-[2/3] relative bg-gradient-to-br from-gray-700 to-gray-900">
              {movie.poster_url ? (
                <img
                  src={movie.poster_url}
                  alt={movie.title}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500">
                  No Image
                </div>
              )}
              
              {/* Overlay on hover */}
              <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-3">
                <p className="text-white text-sm line-clamp-3">{movie.description}</p>
              </div>

              {/* Rating Badge */}
              <div className="absolute top-2 right-2 bg-black/80 px-2 py-1 rounded-lg flex items-center space-x-1">
                <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                <span className="text-white text-xs font-semibold">{movie.rating}</span>
              </div>

              {/* Industry Badge */}
              <div className="absolute top-2 left-2 bg-blue-500 px-2 py-1 rounded text-xs font-semibold text-white">
                {movie.industry}
              </div>
            </div>

            {/* Info */}
            <div className="p-3">
              <h3 className="text-white font-semibold text-sm line-clamp-2 mb-1">
                {movie.title}
              </h3>
              <div className="flex items-center justify-between text-xs text-gray-400">
                <span>{movie.year}</span>
                {movie.popularity && (
                  <span className="flex items-center">
                    <TrendingUp className="w-3 h-3 mr-1" />
                    {Math.round(movie.popularity)}
                  </span>
                )}
              </div>
            </div>
          </button>
          
          {/* Recommend Button */}
          <button
            onClick={(e) => handleRecommend(e, movie)}
            className={`absolute bottom-2 right-2 text-white p-2 rounded-full transition-colors z-10 ${
              isRecommended(movie.id) ? 'bg-green-500' : 'bg-red-500 hover:bg-red-600'
            }`}
            title="Add to My Recommendations"
          >
            {isRecommended(movie.id) ? '✓' : <Heart className="w-4 h-4" />}
          </button>
        </div>
      ))}
    </div>
  )
}
