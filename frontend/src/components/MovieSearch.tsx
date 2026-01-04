'use client'

import React, { useState } from 'react'
import { Search, Heart } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { addRecommendation } from '@/services/api'
import type { Movie } from '@/types'

interface MovieSearchProps {
  movies: Movie[]
  onMovieSelect: (movie: Movie) => void
  selectedMovie: Movie | null
}

export default function MovieSearch({ movies, onMovieSelect, selectedMovie }: MovieSearchProps) {
  const { user } = useAuth()
  const [searchTerm, setSearchTerm] = useState('')
  const [showResults, setShowResults] = useState(false)

  const filteredMovies = movies.filter(movie =>
    movie.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    movie.genres.toLowerCase().includes(searchTerm.toLowerCase())
  ).slice(0, 10)

  const handleMovieClick = (movie: Movie) => {
    onMovieSelect(movie)
    setSearchTerm(movie.title)
    setShowResults(false)
  }

  const handleRecommend = async (e: React.MouseEvent, movie: Movie) => {
    e.stopPropagation()
    
    if (!user) return
    
    try {
      await addRecommendation(user.uid, {
        movie_id: movie.id,
        movie_title: movie.title,
        movie_genres: movie.genres,
        movie_rating: movie.rating,
        movie_year: movie.year,
        movie_description: movie.description,
        source: 'search_recommend'
      })
      
      const recommendedMovies = JSON.parse(localStorage.getItem(`recommended_${user.uid}`) || '[]')
      if (!recommendedMovies.includes(movie.id)) {
        recommendedMovies.push(movie.id)
        localStorage.setItem(`recommended_${user.uid}`, JSON.stringify(recommendedMovies))
      }
      
      const button = e.target as HTMLElement
      button.textContent = '✓'
      button.classList.add('bg-green-500')
    } catch (error) {
      console.error('Error adding recommendation:', error)
    }
  }

  const isRecommended = (movieId: number) => {
    if (!user) return false
    const recommendedMovies = JSON.parse(localStorage.getItem(`recommended_${user.uid}`) || '[]')
    return recommendedMovies.includes(movieId)
  }

  return (
    <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 shadow-xl">
      <h2 className="text-xl font-semibold text-white mb-4">Search Movie</h2>
      <p className="text-gray-300 text-sm mb-4">Search for a movie to get personalized recommendations</p>
      
      <div className="relative">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value)
              setShowResults(true)
            }}
            onBlur={() => setTimeout(() => setShowResults(false), 200)}
            placeholder="Search for a movie..."
            className="w-full pl-10 pr-4 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {showResults && searchTerm && filteredMovies.length > 0 && (
          <div className="absolute z-10 w-full mt-2 bg-gray-800 border border-gray-700 rounded-lg shadow-xl max-h-96 overflow-y-auto">
            {filteredMovies.map((movie) => (
              <div key={movie.id} className="relative">
                <button
                  onClick={() => handleMovieClick(movie)}
                  className="w-full text-left px-4 py-3 hover:bg-gray-700 transition-colors border-b border-gray-700 last:border-b-0"
                >
                  <div className="text-white font-medium pr-12">{movie.title}</div>
                  <div className="text-gray-400 text-sm">{movie.genres} • {movie.year}</div>
                  <div className="flex items-center mt-1">
                    <span className="text-yellow-400 text-sm">⭐ {movie.rating}</span>
                  </div>
                </button>
                <button
                  onClick={(e) => handleRecommend(e, movie)}
                  className={`absolute right-2 top-1/2 transform -translate-y-1/2 p-1 rounded-full transition-colors ${
                    isRecommended(movie.id) ? 'bg-green-500 text-white' : 'bg-red-500 hover:bg-red-600 text-white'
                  }`}
                  title="Add to Recommendations"
                >
                  {isRecommended(movie.id) ? '✓' : <Heart className="w-3 h-3" />}
                </button>
              </div>
            ))}
          </div>
        )}

        {showResults && searchTerm && filteredMovies.length === 0 && (
          <div className="absolute z-10 w-full mt-2 bg-gray-800 border border-gray-700 rounded-lg shadow-xl p-4">
            <p className="text-gray-400 text-sm text-center">No movies found matching "{searchTerm}"</p>
          </div>
        )}
      </div>

      {selectedMovie && (
        <div className="mt-4 p-4 bg-white/5 rounded-lg border border-white/20">
          <h3 className="text-white font-semibold mb-2">{selectedMovie.title}</h3>
          <p className="text-gray-300 text-sm mb-2">{selectedMovie.description}</p>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-400">{selectedMovie.genres}</span>
            <span className="text-yellow-400">⭐ {selectedMovie.rating}</span>
          </div>
        </div>
      )}
    </div>
  )
}
