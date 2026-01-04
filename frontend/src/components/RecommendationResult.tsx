'use client'

import React from 'react'
import { CheckCircle, XCircle, TrendingUp, Film } from 'lucide-react'
import type { RecommendationResponse } from '@/types'
import MovieCard from './MovieCard'

interface RecommendationResultProps {
  recommendation: RecommendationResponse
  onMovieSelect?: (movie: any) => void
}

export default function RecommendationResult({ recommendation, onMovieSelect }: RecommendationResultProps) {
  const { should_watch, confidence, reason, recommended_movies, target_movie } = recommendation

  const handleMovieSelect = (movie: any) => {
    if (onMovieSelect) {
      onMovieSelect(movie)
    }
  }

  return (
    <div className="space-y-6 w-full">
      {/* Main Recommendation Card */}
      <div className={`bg-white/10 backdrop-blur-md rounded-xl p-8 shadow-xl border-2 w-full ${
        should_watch ? 'border-green-500' : 'border-red-500'
      }`}>
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-start space-x-4">
            {should_watch ? (
              <CheckCircle className="w-12 h-12 text-green-400 flex-shrink-0" />
            ) : (
              <XCircle className="w-12 h-12 text-red-400 flex-shrink-0" />
            )}
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">
                {should_watch ? 'Yes, Watch It!' : 'Maybe Skip This One'}
              </h2>
              <p className="text-gray-300">{target_movie?.title}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2 bg-white/10 px-4 py-2 rounded-lg">
            <TrendingUp className="w-5 h-5 text-blue-400" />
            <div>
              <div className="text-xs text-gray-400">Confidence</div>
              <div className="text-lg font-bold text-white">{confidence.toFixed(1)}%</div>
            </div>
          </div>
        </div>

        {target_movie && (
          <div className="bg-white/5 rounded-lg p-4 mb-4">
            <p className="text-gray-300 mb-2">{target_movie.description}</p>
            <div className="flex items-center space-x-4 text-sm">
              <span className="text-gray-400">{target_movie.genres}</span>
              <span className="text-gray-400">•</span>
              <span className="text-gray-400">{target_movie.year}</span>
              <span className="text-gray-400">•</span>
              <span className="text-yellow-400">⭐ {target_movie.rating}</span>
            </div>
          </div>
        )}

        <div className="bg-blue-500/20 border border-blue-500/30 rounded-lg p-4">
          <h3 className="text-white font-semibold mb-2">Analysis</h3>
          <p className="text-gray-200 whitespace-pre-wrap break-words leading-relaxed overflow-auto max-w-full">
            {reason}
          </p>
        </div>
      </div>

      {/* Recommended Movies */}
      {recommended_movies && recommended_movies.length > 0 && (
        <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 shadow-xl">
          <div className="flex items-center space-x-2 mb-6">
            <Film className="w-6 h-6 text-blue-400" />
            <h3 className="text-2xl font-bold text-white">
              Similar Movies You Might Like
            </h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recommended_movies.map((movie) => (
              <MovieCard 
                key={movie.id} 
                movie={movie} 
                onClick={(m) => {
                  // Learn from user interaction
                  handleMovieSelect(m)
                  
                  const modal = document.createElement('div')
                  modal.innerHTML = `
                    <div class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onclick="this.remove()">
                      <div class="bg-gradient-to-br from-purple-900 to-blue-900 rounded-xl p-8 max-w-2xl w-full" onclick="event.stopPropagation()">
                        <h2 class="text-2xl font-bold text-white mb-4">${m.title}</h2>
                        <div class="bg-white/10 rounded-lg p-4 mb-4">
                          <p class="text-gray-300 mb-4">${m.description}</p>
                          <div class="flex items-center space-x-4 text-sm">
                            <span class="text-gray-400">${m.genres}</span>
                            <span class="text-gray-400">•</span>
                            <span class="text-gray-400">${m.year}</span>
                            <span class="text-gray-400">•</span>
                            <span class="text-yellow-400">⭐ ${m.rating}</span>
                          </div>
                        </div>
                        ${m.reason ? `
                          <div class="bg-blue-500/20 border border-blue-500/30 rounded-lg p-4 mb-4">
                            <h3 class="text-blue-300 font-semibold mb-2">💡 Why we recommended this</h3>
                            <p class="text-white">${m.reason}</p>
                          </div>
                        ` : ''}
                        ${m.similarity_score ? `
                          <div class="flex items-center justify-center space-x-2 text-sm">
                            <span class="text-gray-400">Similarity Score:</span>
                            <span class="text-green-400 font-bold">${(m.similarity_score * 100).toFixed(1)}%</span>
                          </div>
                        ` : ''}
                        <button onclick="this.closest('div[onclick]').remove()" class="mt-6 w-full bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold">
                          Close
                        </button>
                      </div>
                    </div>
                  `
                  document.body.appendChild(modal)
                }}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
