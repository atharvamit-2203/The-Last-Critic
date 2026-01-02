'use client'

import { useState } from 'react'
import { Film, Sparkles } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'

export default function LoginPage() {
  const { signInWithGoogle, loading } = useAuth()
  const [error, setError] = useState<string | null>(null)
  const [isSigningIn, setIsSigningIn] = useState(false)

  const handleSignIn = async () => {
    if (isSigningIn) return // Prevent double clicks
    
    try {
      setError(null)
      setIsSigningIn(true)
      await signInWithGoogle()
    } catch (error: any) {
      console.error('Failed to sign in:', error)
      // Only show error if it's not a popup cancellation
      if (error.code !== 'auth/cancelled-popup-request' && error.code !== 'auth/popup-closed-by-user') {
        setError(error.message || 'Failed to sign in. Please try again.')
      }
    } finally {
      setIsSigningIn(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <Film className="w-16 h-16 text-blue-400" />
            <Sparkles className="w-8 h-8 text-yellow-400 ml-2" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">
            AI Movie Recommendations
          </h1>
          <p className="text-gray-300 text-lg">
            Discover your next favorite movie with AI-powered insights
          </p>
        </div>

        {/* Sign In Card */}
        <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 shadow-2xl border border-white/20">
          <h2 className="text-2xl font-bold text-white mb-6 text-center">
            Welcome! 🎬
          </h2>
          
          <p className="text-gray-300 mb-8 text-center">
            Sign in to get personalized movie recommendations based on your taste
          </p>

          <button
            onClick={handleSignIn}
            disabled={loading || isSigningIn}
            className="w-full bg-white hover:bg-gray-100 text-gray-900 font-semibold py-4 px-6 rounded-xl transition-all duration-200 flex items-center justify-center space-x-3 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg className="w-6 h-6" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            <span>{loading || isSigningIn ? 'Signing in...' : 'Sign in with Google'}</span>
          </button>

          {error && (
            <div className="mt-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg">
              <p className="text-red-200 text-sm">{error}</p>
            </div>
          )}

          <div className="mt-6 text-center text-sm text-gray-400">
            <p>✨ Get AI-powered movie analysis</p>
            <p>🎯 Personalized recommendations</p>
            <p>🔍 Search from 255+ movies</p>
            <p className="mt-3 text-green-400">🔐 Stay signed in - no need to login again!</p>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-gray-400 text-sm mt-8">
          Your preferences are saved. You only need to sign in once!
        </p>
      </div>
    </div>
  )
}
