'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'
import { 
  User, 
  signInWithPopup, 
  signOut as firebaseSignOut,
  onAuthStateChanged 
} from 'firebase/auth'
import { auth, googleProvider } from '@/lib/firebase'
import axios from 'axios'

interface AuthContextType {
  user: User | null
  loading: boolean
  signInWithGoogle: () => Promise<void>
  signOut: () => Promise<void>
  hasCompletedOnboarding: () => boolean
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  signInWithGoogle: async () => {},
  signOut: async () => {},
  hasCompletedOnboarding: () => false,
})

export const useAuth = () => useContext(AuthContext)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true) // Start with true for proper initialization
  const [signingIn, setSigningIn] = useState(false)

  useEffect(() => {
    setLoading(true)
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      console.log('Auth state changed:', user ? 'User found' : 'No user')
      if (user) {
        console.log('✓ User restored from persistence:', user.email)
        await syncUserWithBackend(user)
      } else {
        console.log('No persisted user found')
      }
      setUser(user)
      setLoading(false)
      setSigningIn(false)
    })

    return unsubscribe
  }, [])

  const syncUserWithBackend = async (user: User) => {
    try {
      await axios.post('http://localhost:8000/api/auth/user', {
        uid: user.uid,
        email: user.email,
        displayName: user.displayName,
        photoURL: user.photoURL,
      })
    } catch (error) {
      console.error('Error syncing user with backend:', error)
    }
  }

  const signInWithGoogle = async () => {
    if (signingIn) {
      console.log('Sign-in already in progress...')
      return
    }

    try {
      setSigningIn(true)
      console.log('Starting Google sign-in...')
      
      // Ensure Firebase is ready
      const { ensureAuthReady } = await import('@/lib/firebase')
      await ensureAuthReady()
      
      const result = await signInWithPopup(auth, googleProvider)
      console.log('✓ Sign-in successful:', result.user.email)
      await syncUserWithBackend(result.user)
    } catch (error: any) {
      setSigningIn(false)
      
      if (error.code === 'auth/cancelled-popup-request') {
        console.log('Popup request cancelled')
        return
      } else if (error.code === 'auth/popup-closed-by-user') {
        console.log('Popup closed by user')
        return
      }
      
      console.error('Error signing in:', error)
      throw error
    }
  }

  const signOut = async () => {
    try {
      await firebaseSignOut(auth)
      setUser(null)
    } catch (error) {
      console.error('Error signing out:', error)
      throw error
    }
  }

  const hasCompletedOnboarding = () => {
    if (!user) return false
    return localStorage.getItem(`onboarding_${user.uid}`) === 'true'
  }

  return (
    <AuthContext.Provider value={{ user, loading, signInWithGoogle, signOut, hasCompletedOnboarding }}>
      {children}
    </AuthContext.Provider>
  )
}
