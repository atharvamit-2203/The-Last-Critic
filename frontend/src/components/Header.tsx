'use client'

import { Film, User } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'

export default function Header() {
  const { user } = useAuth()
  const router = useRouter()

  const handleAccountClick = () => {
    router.push('/account')
  }

  return (
    <header className="bg-black/30 backdrop-blur-md border-b border-white/10">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Film className="w-10 h-10 text-blue-400" />
            <div>
              <h1 className="text-3xl font-bold text-white">
                The Last Critic
              </h1>
              <p className="text-gray-300 text-sm">
                Your final word on what to watch
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-6">
            <div className="hidden md:flex items-center space-x-6 text-gray-300">
              <span className="text-sm">🎬 Content-Based Filtering</span>
              <span className="text-sm">🤖 TF-IDF • Cosine Similarity</span>
              <span className="text-sm">✨ Your Final Word</span>
            </div>
            
            {user && (
              <button
                onClick={handleAccountClick}
                className="flex items-center space-x-2 bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg transition-all"
              >
                {user.photoURL ? (
                  <img src={user.photoURL} alt={user.displayName || 'User'} className="w-8 h-8 rounded-full" />
                ) : (
                  <User className="w-6 h-6 text-white" />
                )}
                <span className="text-white font-medium hidden md:block">{user.displayName?.split(' ')[0]}</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
