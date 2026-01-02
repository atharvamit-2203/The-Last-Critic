'use client'

import React from 'react'
import { Star, Calendar } from 'lucide-react'
import type { UserPreferences } from '@/types'

interface PreferencesFormProps {
  preferences: UserPreferences
  onPreferencesChange: (preferences: UserPreferences) => void
  onSearch?: () => void
  isSearching?: boolean
}

const GENRES = ['Action', 'Comedy', 'Drama', 'Horror', 'Romance', 'Sci-Fi', 'Thriller', 'Crime', 'Adventure', 'Animation']
const DECADES = [1970, 1980, 1990, 2000, 2010, 2020]

export default function PreferencesForm({ preferences, onPreferencesChange, onSearch, isSearching }: PreferencesFormProps) {
  const handleGenreToggle = (genre: string) => {
    const newGenres = preferences.favorite_genres.includes(genre)
      ? preferences.favorite_genres.filter(g => g !== genre)
      : [...preferences.favorite_genres, genre]
    
    onPreferencesChange({
      ...preferences,
      favorite_genres: newGenres
    })
  }

  return (
    <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 shadow-xl">
      <h2 className="text-xl font-semibold text-white mb-4">Your Preferences</h2>
      <p className="text-gray-300 text-sm mb-4">Your preferences affect the recommendations you receive</p>
      
      {/* Favorite Genres */}
      <div className="mb-6">
        <label className="block text-white text-sm font-medium mb-3">
          Favorite Genres
        </label>
        <div className="flex flex-wrap gap-2">
          {GENRES.map(genre => (
            <button
              key={genre}
              onClick={() => handleGenreToggle(genre)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                preferences.favorite_genres.includes(genre)
                  ? 'bg-blue-500 text-white'
                  : 'bg-white/20 text-gray-300 hover:bg-white/30'
              }`}
            >
              {genre}
            </button>
          ))}
        </div>
      </div>

      {/* Minimum Rating */}
      <div className="mb-6">
        <label className="block text-white text-sm font-medium mb-2">
          <Star className="inline w-4 h-4 mr-1" />
          Minimum Rating: {preferences.min_rating}
        </label>
        <input
          type="range"
          min="0"
          max="10"
          step="0.5"
          value={preferences.min_rating}
          onChange={(e) => onPreferencesChange({
            ...preferences,
            min_rating: parseFloat(e.target.value)
          })}
          className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer slider"
          style={{
            background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${(preferences.min_rating / 10) * 100}%, rgba(255,255,255,0.2) ${(preferences.min_rating / 10) * 100}%, rgba(255,255,255,0.2) 100%)`
          }}
        />
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>0</span>
          <span>5</span>
          <span>10</span>
        </div>
      </div>

      {/* Preferred Decade */}
      <div>
        <label className="block text-white text-sm font-medium mb-2">
          <Calendar className="inline w-4 h-4 mr-1" />
          Preferred Decade
        </label>
        <select
          value={preferences.preferred_decade}
          onChange={(e) => onPreferencesChange({
            ...preferences,
            preferred_decade: parseInt(e.target.value)
          })}
          className="w-full px-4 py-2 bg-white/20 border border-white/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {DECADES.map(decade => (
            <option key={decade} value={decade} className="bg-gray-800">
              {decade}s
            </option>
          ))}
        </select>
      </div>

      {/* Search Button */}
      {onSearch && (
        <button
          onClick={onSearch}
          disabled={isSearching}
          className="w-full mt-6 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 disabled:from-gray-500 disabled:to-gray-600 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 flex items-center justify-center space-x-2"
        >
          {isSearching ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>Searching...</span>
            </>
          ) : (
            <>
              <span>🔍</span>
              <span>Find Movies Matching My Preferences</span>
            </>
          )}
        </button>
      )}
    </div>
  )
}
