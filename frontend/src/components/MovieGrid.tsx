'use client'

import React from 'react'
import { Star, TrendingUp } from 'lucide-react'

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
        <button
          key={movie.id}
          onClick={() => onMovieClick(movie)}
          className="group relative bg-gray-800/50 rounded-xl overflow-hidden hover:ring-2 hover:ring-blue-500 transition-all hover:scale-105 cursor-pointer"
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
      ))}
    </div>
  )
}
