'use client'

import React, { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { getUserRecommendations } from '@/services/api'
import { Star, Calendar, Tag, Heart } from 'lucide-react'

interface Recommendation {
  id: string
  movieId: number
  movieTitle: string
  movieGenres: string
  movieRating: number
  movieYear: number
  movieDescription: string
  source: string
  recommendedAt: any
}

export default function UserProfile() {
  const { user } = useAuth()
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (user) {
      loadRecommendations()
    }
  }, [user])

  const loadRecommendations = async () => {
    if (!user) return

    try {
      setLoading(true)
      const data = await getUserRecommendations(user.uid)
      setRecommendations(data.recommendations || [])
    } catch (err) {
      console.error('Error loading recommendations:', err)
      setError('Failed to load recommendations')
    } finally {
      setLoading(false)
    }
  }

  if (!user) {
    return (
      <div className="text-center py-12 text-gray-400">
        Please sign in to view your profile
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Profile Header */}
      <div className="bg-white/10 backdrop-blur-md rounded-xl p-6">
        <div className="flex items-center space-x-4">
          {user.photoURL && (
            <img
              src={user.photoURL}
              alt={user.displayName || 'User'}
              className="w-16 h-16 rounded-full"
            />
          )}
          <div>
            <h2 className="text-2xl font-bold text-white">
              {user.displayName || 'Movie Enthusiast'}
            </h2>
            <p className="text-gray-300">{user.email}</p>
          </div>
        </div>
      </div>

      {/* Recommendations Section */}
      <div className="bg-white/10 backdrop-blur-md rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-white flex items-center">
            <Heart className="w-5 h-5 mr-2 text-red-500" />
            My Recommended Movies ({recommendations.length})
          </h3>
          <button
            onClick={loadRecommendations}
            className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
          >
            Refresh
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
            <p className="text-white text-lg">Loading your recommendations...</p>
          </div>
        ) : error ? (
          <div className="bg-red-500 text-white p-4 rounded-lg">
            {error}
          </div>
        ) : recommendations.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <Heart className="w-16 h-16 mx-auto mb-4 text-gray-600" />
            <p className="text-lg mb-2">No recommendations yet</p>
            <p className="text-sm">Start exploring movies and click the heart button to add them to your list!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recommendations.map((rec) => (
              <div
                key={rec.id}
                className="bg-white/5 rounded-lg p-4 hover:bg-white/10 transition-all border border-white/10"
              >
                <h4 className="text-white font-bold text-lg mb-2">{rec.movieTitle}</h4>
                <p className="text-gray-300 text-sm mb-3 line-clamp-3">{rec.movieDescription}</p>
                
                {/* Movie Details */}
                <div className="space-y-2 mb-3">
                  <div className="flex items-center text-sm text-gray-400">
                    <Tag className="w-4 h-4 mr-2" />
                    {rec.movieGenres}
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center text-gray-400">
                      <Calendar className="w-4 h-4 mr-2" />
                      {rec.movieYear}
                    </div>
                    <div className="flex items-center text-yellow-400">
                      <Star className="w-4 h-4 mr-1 fill-yellow-400" />
                      {rec.movieRating}
                    </div>
                  </div>
                </div>

                {/* Source Badge */}
                <div className="flex items-center justify-between">
                  <span className="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded">
                    {rec.source === 'latest_movies' ? 'Latest Movies' : 
                     rec.source === 'user_click' ? 'Search & Recommend' : 
                     rec.source === 'onboarding' ? 'Onboarding' : 'Other'}
                  </span>
                  <span className="text-xs text-gray-500">
                    {rec.recommendedAt?.toDate ? 
                      rec.recommendedAt.toDate().toLocaleDateString() : 
                      'Recently added'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}