import React from 'react'
import type { Movie } from '@/types'

interface MovieCardProps {
  movie: Movie
  onClick?: (movie: Movie) => void
}

export default function MovieCard({ movie, onClick }: MovieCardProps) {
  return (
    <div 
      onClick={() => onClick?.(movie)}
      className="bg-white/5 hover:bg-white/10 rounded-lg p-4 transition-all cursor-pointer border border-white/10 hover:border-white/30 hover:scale-105"
    >
      <h4 className="text-white font-semibold mb-2">{movie.title}</h4>
      <p className="text-gray-300 text-sm mb-3 line-clamp-2">{movie.description}</p>
      <div className="flex items-center justify-between">
        <span className="text-gray-400 text-xs">{movie.genres}</span>
        <div className="flex items-center space-x-2">
          <span className="text-gray-400 text-xs">{movie.year}</span>
          <span className="text-yellow-400 text-sm">⭐ {movie.rating}</span>
        </div>
      </div>
      {movie.reason && (
        <div className="mt-3 pt-3 border-t border-white/10">
          <p className="text-blue-300 text-xs">💡 Click to see why we recommended this</p>
        </div>
      )}
    </div>
  )
}
