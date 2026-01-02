'use client'

import React from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { LogIn, LogOut, User } from 'lucide-react'

export default function AuthButton() {
  const { user, loading, signInWithGoogle, signOut } = useAuth()

  if (loading) {
    return (
      <div className="flex items-center space-x-2">
        <div className="w-8 h-8 rounded-full bg-white/20 animate-pulse"></div>
      </div>
    )
  }

  if (user) {
    return (
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          {user.photoURL ? (
            <img
              src={user.photoURL}
              alt={user.displayName || 'User'}
              className="w-8 h-8 rounded-full border-2 border-white/20"
            />
          ) : (
            <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center">
              <User className="w-5 h-5 text-white" />
            </div>
          )}
          <span className="text-white text-sm hidden md:inline">
            {user.displayName || user.email}
          </span>
        </div>
        <button
          onClick={signOut}
          className="flex items-center space-x-2 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-300 rounded-lg transition-colors border border-red-500/30"
        >
          <LogOut className="w-4 h-4" />
          <span className="hidden md:inline">Sign Out</span>
        </button>
      </div>
    )
  }

  return (
    <button
      onClick={signInWithGoogle}
      className="flex items-center space-x-2 px-6 py-3 bg-white hover:bg-gray-100 text-gray-900 rounded-lg transition-colors font-semibold shadow-lg"
    >
      <LogIn className="w-5 h-5" />
      <span>Sign in with Google</span>
    </button>
  )
}
