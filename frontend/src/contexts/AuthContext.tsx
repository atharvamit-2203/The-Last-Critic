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
  const [loading, setLoading] = useState(true)
  const [signingIn, setSigningIn] = useState(false) // Prevent multiple popups

  useEffect(() => {
    // Set a timeout to ensure loading doesn't hang forever
    const loadingTimeout = setTimeout(() => {
      if (loading) {
        console.log('Auth loading timeout - forcing completion')
        setLoading(false)
      }
    }, 3000) // 3 second timeout

    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      clearTimeout(loadingTimeout) // Clear timeout if auth resolves
      
      if (user) {
        await syncUserWithBackend(user)
        console.log('✓ User authenticated:', user.email)
        
        // Check onboarding status
        const onboardingStatus = localStorage.getItem(`onboarding_${user.uid}`)
        if (onboardingStatus === 'true') {
          console.log('✓ Onboarding already completed')
        } else {
          console.log('⚠ Onboarding not completed yet')
        }
      } else {
        console.log('No user authenticated')
      }
      setUser(user)
      setLoading(false)
      setSigningIn(false) // Reset signing in state
    })

    return () => {
      clearTimeout(loadingTimeout)
      unsubscribe()
    }
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
    // Prevent multiple simultaneous sign-in attempts
    if (signingIn) {
      console.log('Sign-in already in progress...')
      return
    }

    try {
      setSigningIn(true)
      const result = await signInWithPopup(auth, googleProvider)
      await syncUserWithBackend(result.user)
    } catch (error: any) {
      setSigningIn(false)
      
      // Handle specific Firebase auth errors gracefully
      if (error.code === 'auth/cancelled-popup-request') {
        console.log('Popup request cancelled - this is normal if you clicked sign in multiple times')
        return // Don't throw error, just ignore it
      } else if (error.code === 'auth/popup-closed-by-user') {
        console.log('Popup closed by user')
        return // User intentionally closed it
      }
      
      console.error('Error signing in with Google:', error)
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
