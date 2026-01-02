'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Film, User, LogOut, Calendar, Star, Heart } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'

export default function AccountPage() {
  const { user, signOut, authLoading } = useAuth()
  const router = useRouter()
  const [favoriteMovies, setFavoriteMovies] = useState<string[]>([])
  const [totalRecommendations, setTotalRecommendations] = useState(0)

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/')
    }
  }, [user, authLoading, router])

  useEffect(() => {
    if (user) {
      // Load user's favorite movies from localStorage
      const favorites = localStorage.getItem('favoriteMovies')
      if (favorites) {
        setFavoriteMovies(JSON.parse(favorites))
      }

      // Calculate total recommendations received
      const onboardingComplete = localStorage.getItem('hasCompletedOnboarding')
      if (onboardingComplete === 'true') {
        setTotalRecommendations(20) // Initial recommendations
      }
    }
  }, [user])

  const handleLogout = async () => {
    try {
      // Clear onboarding status
      localStorage.removeItem('hasCompletedOnboarding')
      localStorage.removeItem('favoriteMovies')
      
      // Sign out
      await signOut()
      
      // Broadcast logout event to other tabs
      localStorage.setItem('logout-event', Date.now().toString())
      
      // Redirect to home
      window.close()
      router.push('/')
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  if (authLoading || !user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    )
  }

  const accountCreatedDate = user.metadata?.creationTime 
    ? new Date(user.metadata.creationTime).toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      })
    : 'Unknown'

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      {/* Header */}
      <header className="bg-black/30 backdrop-blur-md border-b border-white/10">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center space-x-3">
            <Film className="w-10 h-10 text-blue-400" />
            <div>
              <h1 className="text-3xl font-bold text-white">My Account</h1>
              <p className="text-gray-300 text-sm">Manage your profile and preferences</p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Profile Card */}
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
            <div className="flex flex-col md:flex-row items-center md:items-start space-y-6 md:space-y-0 md:space-x-8">
              {/* Avatar */}
              <div className="flex-shrink-0">
                {user.photoURL ? (
                  <img
                    src={user.photoURL}
                    alt={user.displayName || 'User'}
                    className="w-32 h-32 rounded-full border-4 border-blue-500"
                  />
                ) : (
                  <div className="w-32 h-32 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                    <User className="w-16 h-16 text-white" />
                  </div>
                )}
              </div>

              {/* User Info */}
              <div className="flex-1 space-y-4 text-center md:text-left">
                <h2 className="text-3xl font-bold text-white">{user.displayName || 'User'}</h2>
                <p className="text-gray-300">{user.email}</p>
                
                <div className="flex flex-wrap gap-4 justify-center md:justify-start">
                  <div className="bg-white/5 rounded-lg px-4 py-2">
                    <div className="flex items-center space-x-2">
                      <Calendar className="w-4 h-4 text-blue-400" />
                      <span className="text-gray-300 text-sm">Joined {accountCreatedDate}</span>
                    </div>
                  </div>
                  <div className="bg-white/5 rounded-lg px-4 py-2">
                    <div className="flex items-center space-x-2">
                      <Star className="w-4 h-4 text-yellow-400" />
                      <span className="text-gray-300 text-sm">{totalRecommendations} Recommendations</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Details Card */}
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
            <h3 className="text-2xl font-bold text-white mb-6">Account Details</h3>
            <div className="space-y-4">
              <div className="bg-white/5 rounded-lg p-4">
                <p className="text-gray-400 text-sm mb-1">Full Name</p>
                <p className="text-white font-medium">{user.displayName || 'Not provided'}</p>
              </div>

              <div className="bg-white/5 rounded-lg p-4">
                <p className="text-gray-400 text-sm mb-1">Email Address</p>
                <p className="text-white font-medium">{user.email}</p>
              </div>

              <div className="bg-white/5 rounded-lg p-4">
                <p className="text-gray-400 text-sm mb-1">User ID</p>
                <p className="text-white font-mono text-sm break-all">{user.uid}</p>
              </div>

              <div className="bg-white/5 rounded-lg p-4">
                <p className="text-gray-400 text-sm mb-1">Email Verified</p>
                <p className="text-white font-medium">{user.emailVerified ? 'Yes ✓' : 'No'}</p>
              </div>
            </div>
          </div>

          {/* Favorite Movies Card */}
          {favoriteMovies.length > 0 && (
            <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
              <div className="flex items-center space-x-2 mb-6">
                <Heart className="w-6 h-6 text-red-400" />
                <h3 className="text-2xl font-bold text-white">Your Favorite Movies</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {favoriteMovies.map((movie, index) => (
                  <div key={index} className="bg-white/5 rounded-lg p-4">
                    <p className="text-white font-medium">{movie}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-4">
            <button
              onClick={() => router.push('/')}
              className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-200"
            >
              Back to App
            </button>
            <button
              onClick={handleLogout}
              className="flex-1 bg-red-500 hover:bg-red-600 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2"
            >
              <LogOut className="w-5 h-5" />
              <span>Log Out</span>
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}
