'use client'

import React, { useState } from 'react'
import { Search, Sparkles, ArrowRight, Plus, X } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { getAllMovies } from '@/services/api'
import type { Movie } from '@/types'

interface OnboardingPageProps {
  onComplete: (favoriteMovies: string[]) => void
}

export default function OnboardingPage({ onComplete }: OnboardingPageProps) {
  const { user } = useAuth()
  const [searchQuery, setSearchQuery] = useState('')
  const [favoriteMovies, setFavoriteMovies] = useState<string[]>([])
  const [suggestions, setSuggestions] = useState<Movie[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)

  // Load previously saved favorites if they exist
  React.useEffect(() => {
    if (user) {
      const savedFavorites = localStorage.getItem(`favoriteMovies_${user.uid}`)
      if (savedFavorites) {
        try {
          const favorites = JSON.parse(savedFavorites)
          if (favorites.length > 0) {
            setFavoriteMovies(favorites)
          }
        } catch (err) {
          console.error('Error loading saved favorites:', err)
        }
      }
    }
  }, [user])

  const handleSearch = async (query: string) => {
    setSearchQuery(query)
    
    if (query.length >= 2) {
      try {
        const movies = await getAllMovies(100, query)
        setSuggestions(movies.slice(0, 10))
        setShowSuggestions(true)
      } catch (error) {
        console.error('Error searching movies:', error)
      }
    } else {
      setSuggestions([])
      setShowSuggestions(false)
    }
  }

  const handleAddMovie = (movieTitle: string) => {
    if (!favoriteMovies.includes(movieTitle) && favoriteMovies.length < 5 && movieTitle.trim()) {
      setFavoriteMovies([...favoriteMovies, movieTitle.trim()])
      setSearchQuery('')
      setSuggestions([])
      setShowSuggestions(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && searchQuery.trim()) {
      // If there are suggestions, add the first one, otherwise add the typed text
      const movieToAdd = suggestions.length > 0 ? suggestions[0].title : searchQuery
      handleAddMovie(movieToAdd)
    }
  }

  const handleRemoveMovie = (movieTitle: string) => {
    setFavoriteMovies(favoriteMovies.filter(m => m !== movieTitle))
  }

  const handleContinue = () => {
    if (favoriteMovies.length > 0) {
      // Save to localStorage for persistence
      if (user) {
        localStorage.setItem(`favoriteMovies_${user.uid}`, JSON.stringify(favoriteMovies))
      }
      onComplete(favoriteMovies)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        {/* Welcome Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <Sparkles className="w-12 h-12 text-yellow-400" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">
            Welcome, {user?.displayName?.split(' ')[0]}! 👋
          </h1>
          <p className="text-gray-300 text-lg">
            Tell us about your favorite movies to get personalized recommendations
          </p>
        </div>

        {/* Main Card */}
        <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 shadow-2xl border border-white/20">
          <div className="mb-6">
            <label className="block text-white font-semibold mb-3 text-lg">
              What are your favorite movies? (Add 1-5 movies)
            </label>
            
            {/* Search Input */}
            <div className="relative">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => handleSearch(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type movie name and press Enter, or select from suggestions..."
                  className="w-full pl-12 pr-4 py-4 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={favoriteMovies.length >= 5}
                />
              </div>

              {/* Suggestions Dropdown */}
              {showSuggestions && suggestions.length > 0 && (
                <div className="absolute z-10 w-full mt-2 bg-gray-800 border border-gray-700 rounded-xl shadow-xl max-h-60 overflow-y-auto">
                  {suggestions.map((movie) => (
                    <button
                      key={movie.id}
                      onClick={() => handleAddMovie(movie.title)}
                      disabled={favoriteMovies.includes(movie.title)}
                      className="w-full px-4 py-3 text-left hover:bg-gray-700 text-white flex items-center justify-between disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      <div>
                        <div className="font-semibold">{movie.title}</div>
                        <div className="text-sm text-gray-400">
                          {movie.year} • {movie.genres}
                        </div>
                      </div>
                      {!favoriteMovies.includes(movie.title) && (
                        <Plus className="w-5 h-5 text-blue-400" />
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Selected Movies */}
          {favoriteMovies.length > 0 && (
            <div className="mb-6">
              <h3 className="text-white font-semibold mb-3">
                Your Favorites ({favoriteMovies.length}/5)
              </h3>
              <div className="space-y-2">
                {favoriteMovies.map((movie, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between bg-blue-500/20 border border-blue-500/30 rounded-lg p-3"
                  >
                    <span className="text-white font-medium">{movie}</span>
                    <button
                      onClick={() => handleRemoveMovie(movie)}
                      className="text-red-400 hover:text-red-300 transition-colors"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Info Box */}
          <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4 mb-6">
            <p className="text-blue-200 text-sm">
              💡 <strong>Tip:</strong> Add movies from different genres to get better recommendations.
              We'll analyze your taste and suggest 20 movies you might love!
            </p>
          </div>

          {/* Continue Button */}
          <button
            onClick={handleContinue}
            disabled={favoriteMovies.length === 0}
            className="w-full bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed disabled:from-gray-500 disabled:to-gray-600"
          >
            <span>
              {favoriteMovies.length === 0
                ? 'Add at least 1 movie to continue'
                : `Continue with ${favoriteMovies.length} ${favoriteMovies.length === 1 ? 'movie' : 'movies'}`}
            </span>
            <ArrowRight className="w-5 h-5" />
          </button>

          {/* Auto-Complete Hint */}
          {favoriteMovies.length > 0 && (
            <div className="mt-3 text-center">
              <p className="text-green-400 text-sm">
                ✓ Your preferences are saved and will be remembered
              </p>
            </div>
          )}

          {/* Skip Option */}
          <button
            onClick={() => onComplete([])}
            className="w-full mt-3 text-gray-400 hover:text-white transition-colors py-2"
          >
            Skip for now
          </button>
        </div>
      </div>
    </div>
  )
}
