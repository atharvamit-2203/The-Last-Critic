'use client'

import React, { useState } from 'react'
import { Search } from 'lucide-react'
import type { Movie } from '@/types'

interface MovieSearchProps {
  movies: Movie[]
  onMovieSelect: (movie: Movie) => void
  selectedMovie: Movie | null
}

export default function MovieSearch({ movies, onMovieSelect, selectedMovie }: MovieSearchProps) {
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
            onFocus={() => setShowResults(true)}
            placeholder="Search for a movie..."
            className="w-full pl-10 pr-4 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {showResults && searchTerm && filteredMovies.length > 0 && (
          <div className="absolute z-10 w-full mt-2 bg-gray-800 border border-gray-700 rounded-lg shadow-xl max-h-96 overflow-y-auto">
            {filteredMovies.map((movie) => (
              <button
                key={movie.id}
                onClick={() => handleMovieClick(movie)}
                className="w-full text-left px-4 py-3 hover:bg-gray-700 transition-colors border-b border-gray-700 last:border-b-0"
              >
                <div className="text-white font-medium">{movie.title}</div>
                <div className="text-gray-400 text-sm">{movie.genres} • {movie.year}</div>
                <div className="flex items-center mt-1">
                  <span className="text-yellow-400 text-sm">⭐ {movie.rating}</span>
                </div>
              </button>
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
