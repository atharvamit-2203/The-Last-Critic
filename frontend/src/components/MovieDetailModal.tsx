'use client'

import React, { useState } from 'react'
import { X, Star, TrendingUp, Users, Sparkles, ExternalLink } from 'lucide-react'
import { analyzeMovie } from '@/services/api'

interface Movie {
  id: number
  title: string
  original_title?: string
  description: string
  rating: number
  year: string
  genres: string
  industry: string
  poster_url?: string
  backdrop_url?: string
  popularity?: number
}

interface MovieDetailModalProps {
  movie: Movie
  onClose: () => void
}

export default function MovieDetailModal({ movie, onClose }: MovieDetailModalProps) {
  const [analysis, setAnalysis] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)
  const [hasLoaded, setHasLoaded] = useState(false)

  React.useEffect(() => {
    // Only load once per movie
    if (!hasLoaded) {
      loadAnalysis()
    }
  }, [movie.id]) // Use movie.id instead of movie object

  const loadAnalysis = async () => {
    if (loading) return // Prevent multiple simultaneous calls
    
    setLoading(true)
    setHasLoaded(false)
    try {
      const result = await analyzeMovie({
        movie_title: movie.title,
        movie_year: movie.year
      })
      console.log('Analysis result:', result)
      setAnalysis(result)
      setHasLoaded(true)
    } catch (error) {
      console.error('Error analyzing movie:', error)
      setAnalysis({
        error: true,
        message: 'Failed to load analysis. Please check if the backend is running and Ollama is available.'
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-gray-700 shadow-2xl">
        {/* Header with Backdrop */}
        <div className="relative h-64 bg-gradient-to-b from-transparent to-gray-900">
          {movie.backdrop_url ? (
            <img
              src={movie.backdrop_url}
              alt={movie.title}
              className="w-full h-full object-cover opacity-40"
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-blue-900 to-purple-900" />
          )}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 bg-black/50 hover:bg-black/70 text-white p-2 rounded-full transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
          
          <div className="absolute bottom-0 left-0 right-0 p-6">
            <div className="flex items-end space-x-6">
              {movie.poster_url && (
                <img
                  src={movie.poster_url}
                  alt={movie.title}
                  className="w-32 h-48 object-cover rounded-lg shadow-2xl border-2 border-white/20"
                />
              )}
              <div className="flex-1">
                <h2 className="text-4xl font-bold text-white mb-2">{movie.title}</h2>
                {movie.original_title && movie.original_title !== movie.title && (
                  <p className="text-gray-300 text-lg mb-2">{movie.original_title}</p>
                )}
                <div className="flex items-center space-x-4 text-sm text-gray-300">
                  <span className="flex items-center">
                    <Star className="w-4 h-4 text-yellow-400 mr-1" />
                    {movie.rating}/10
                  </span>
                  <span>{movie.year}</span>
                  <span className="px-3 py-1 bg-blue-500/30 rounded-full">{movie.industry}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Overview */}
          <div>
            <h3 className="text-xl font-semibold text-white mb-2">Overview</h3>
            <div className="relative">
              <p className={`text-gray-300 leading-relaxed ${!isExpanded ? 'line-clamp-3' : ''}`}>
                {movie.description}
              </p>
              {movie.description && movie.description.length > 200 && (
                <button
                  onClick={() => setIsExpanded(!isExpanded)}
                  className="mt-2 text-blue-400 hover:text-blue-300 text-sm font-semibold transition-colors"
                >
                  {isExpanded ? 'Show Less' : 'More'}
                </button>
              )}
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {movie.genres.split(',').map((genre, idx) => (
                <span key={idx} className="px-3 py-1 bg-purple-500/20 text-purple-300 rounded-full text-sm">
                  {genre.trim()}
                </span>
              ))}
            </div>
          </div>

          {/* AI Analysis */}
          <div className="border-t border-gray-700 pt-6">
            <div className="flex items-center space-x-2 mb-4">
              <Sparkles className="w-6 h-6 text-blue-400" />
              <h3 className="text-2xl font-semibold text-white">AI-Powered Review Analysis</h3>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
              </div>
            ) : analysis ? (
              analysis.error ? (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-6">
                  <p className="text-red-300">{analysis.message || 'Unable to load analysis'}</p>
                  <button
                    onClick={loadAnalysis}
                    className="mt-4 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors text-sm"
                  >
                    Retry
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Sources */}
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <h4 className="text-sm font-semibold text-gray-400 mb-2 flex items-center">
                      <ExternalLink className="w-4 h-4 mr-2" />
                      Sources Analyzed
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {analysis.sources_analyzed?.map((source: string, idx: number) => (
                        <span key={idx} className="text-xs px-2 py-1 bg-gray-700 text-gray-300 rounded">
                          {source}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Analysis Content */}
                  <div className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-lg p-6 border border-blue-500/20">
                    <div className="prose prose-invert max-w-none">
                      <div className="text-gray-200 whitespace-pre-wrap leading-relaxed">
                        {analysis.analysis}
                      </div>
                    </div>
                  </div>

                  {/* Quick Stats */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
                      <div className="flex items-center space-x-2 mb-2">
                        <Users className="w-5 h-5 text-green-400" />
                        <h4 className="text-sm font-semibold text-green-400">Mass Appeal</h4>
                      </div>
                      <p className="text-xs text-gray-300">
                        How well it resonates with general audiences
                      </p>
                    </div>
                    <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-4">
                      <div className="flex items-center space-x-2 mb-2">
                        <TrendingUp className="w-5 h-5 text-purple-400" />
                        <h4 className="text-sm font-semibold text-purple-400">Class Appeal</h4>
                      </div>
                      <p className="text-xs text-gray-300">
                        How well critics and cinephiles appreciate it
                      </p>
                    </div>
                  </div>
                </div>
              )
            ) : (
              <p className="text-gray-400">Unable to load analysis</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
