'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import LoginPage from '@/components/LoginPage'
import OnboardingPage from '@/components/OnboardingPage'
import MovieSearch from '@/components/MovieSearch'
import RecommendationResult from '@/components/RecommendationResult'
import PreferencesForm from '@/components/PreferencesForm'
import Header from '@/components/Header'
import MovieGrid from '@/components/MovieGrid'
import MovieDetailModal from '@/components/MovieDetailModal'
import { getMovies, getRecommendations, getLatestMovies, searchMoviesByPreferences } from '@/services/api'
import type { Movie, UserPreferences, RecommendationResponse } from '@/types'

export default function Home() {
  const { user, loading: authLoading, signOut } = useAuth()
  const [hasCompletedOnboarding, setHasCompletedOnboarding] = useState(false)
  const [recommendedMovies, setRecommendedMovies] = useState<Movie[]>([])
  const [movies, setMovies] = useState<Movie[]>([])
  const [latestMovies, setLatestMovies] = useState<any[]>([])
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null)
  const [selectedLatestMovie, setSelectedLatestMovie] = useState<any>(null)
  const [preferences, setPreferences] = useState<UserPreferences>({
    favorite_genres: [],
    min_rating: 7.0,
    preferred_decade: 2000
  })
  const [recommendation, setRecommendation] = useState<RecommendationResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'latest' | 'search'>('latest')
  const [preferenceSearchResults, setPreferenceSearchResults] = useState<Movie[]>([])
  const [isSearchingByPreferences, setIsSearchingByPreferences] = useState(false)
  const [loadingStates, setLoadingStates] = useState({
    movies: false,
    latestMovies: false,
    recommendations: false
  })

  const loadMovies = async () => {
    if (loadingStates.movies || movies.length > 0) return
    
    setLoadingStates(prev => ({ ...prev, movies: true }))
    try {
      const data = await getMovies()
      setMovies(data)
      setError(null)
    } catch (err) {
      console.error('Error loading movies:', err)
    } finally {
      setLoadingStates(prev => ({ ...prev, movies: false }))
    }
  }

  const loadLatestMovies = async () => {
    if (loadingStates.latestMovies) return
    
    setLoadingStates(prev => ({ ...prev, latestMovies: true }))
    try {
      setError(null)
      const data = await getLatestMovies()
      setLatestMovies(data.movies || [])
      if (data.movies && data.movies.length > 0) {
        console.log(`✓ Loaded ${data.movies.length} latest movies`)
      }
    } catch (err: any) {
      console.error('Error loading latest movies:', err)
      const errorMsg = err.message || 'Failed to load latest movies'
      setError(errorMsg)
      
      // Auto-clear error after 5 seconds
      setTimeout(() => setError(null), 5000)
      
      // Use fallback from our database immediately
      try {
        const fallbackMovies = await getMovies(25)
        setLatestMovies(fallbackMovies.map(m => ({
          id: m.id,
          title: m.title,
          description: m.description,
          rating: m.rating,
          year: m.year.toString(),
          genres: m.genres,
          industry: 'International',
          popularity: 1000
        })))
        console.log(`✓ Using ${fallbackMovies.length} movies from database as fallback`)
      } catch (fallbackErr) {
        console.error('Fallback also failed:', fallbackErr)
      }
    } finally {
      setLoadingStates(prev => ({ ...prev, latestMovies: false }))
    }
  }

  // Load latest movies immediately on component mount
  useEffect(() => {
    loadLatestMovies()
  }, [])

  // Check onboarding status and load movies
  useEffect(() => {
    if (user) {
      const onboardingComplete = localStorage.getItem(`onboarding_${user.uid}`)
      const isComplete = onboardingComplete === 'true'
      setHasCompletedOnboarding(isComplete)
      
      // Load recommendation movies if onboarding is complete
      if (isComplete) {
        loadMovies()
        
        // Clear cache and force fresh load of latest movies
        const { requestCache } = require('@/utils/requestCache')
        requestCache.clear('latest')
        setLatestMovies([])
        loadLatestMovies()
        
        // Load personalized recommendations from localStorage
        const savedRecommendations = localStorage.getItem(`recommendations_${user.uid}`)
        if (savedRecommendations) {
          try {
            const recommendations = JSON.parse(savedRecommendations)
            setRecommendedMovies(recommendations)
          } catch (err) {
            console.error('Error loading saved recommendations:', err)
          }
        }
      }
    }
  }, [user])

  // Listen for logout events from other tabs
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'logout-event') {
        // Another tab logged out, sign out this tab too
        signOut()
      }
    }

    window.addEventListener('storage', handleStorageChange)
    return () => window.removeEventListener('storage', handleStorageChange)
  }, [signOut])

  const handleOnboardingComplete = async (favoriteMovies: string[]) => {
    if (user) {
      localStorage.setItem(`onboarding_${user.uid}`, 'true')
      setHasCompletedOnboarding(true)
      
      // Get recommendations based on favorite movies
      if (favoriteMovies.length > 0) {
        try {
          setLoading(true)
          const allMovies = await getMovies(255)
          
          // Get recommendations for each favorite movie
          const allRecommendations: Movie[] = []
          for (const movieTitle of favoriteMovies) {
            try {
              const result = await getRecommendations({
                movie_title: movieTitle,
                user_preferences: preferences,
                num_recommendations: 5
              })
              if (result.recommended_movies) {
                allRecommendations.push(...result.recommended_movies)
              }
            } catch (err) {
              console.error(`Error getting recommendations for ${movieTitle}:`, err)
            }
          }
          
          // Remove duplicates and limit to 20
          const uniqueMovies = Array.from(
            new Map(allRecommendations.map(m => [m.id, m])).values()
          ).slice(0, 20)
          
          setRecommendedMovies(uniqueMovies)
          
          // Save recommendations to localStorage for future visits
          if (user) {
            localStorage.setItem(`recommendations_${user.uid}`, JSON.stringify(uniqueMovies))
          }
        } catch (err) {
          console.error('Error loading recommendations:', err)
        } finally {
          setLoading(false)
        }
      }
      
      // Reload latest movies to replace fallback data if needed
      if (latestMovies.length === 0) {
        loadLatestMovies()
      }
    }
  }

  // Show login page if not authenticated
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
          <div className="text-white text-xl">Loading...</div>
          <div className="text-gray-400 text-sm mt-2">Initializing authentication</div>
        </div>
      </div>
    )
  }

  if (!user) {
    return <LoginPage />
  }

  // Show onboarding if not completed
  if (!hasCompletedOnboarding) {
    return <OnboardingPage onComplete={handleOnboardingComplete} />
  }

  const handleMovieSelect = async (movie: Movie) => {
    setSelectedMovie(movie)
    setError(null)
    setLoading(true)

    // Learn from this selection
    await learnFromUserInteraction(movie)

    try {
      const result = await getRecommendations({
        movie_title: movie.title,
        user_preferences: preferences,
        num_recommendations: 5
      })
      setRecommendation(result)
    } catch (err) {
      console.error('Error getting recommendations:', err)
      setError('Failed to get recommendations')
    } finally {
      setLoading(false)
    }
  }

  const handlePreferencesChange = async (newPreferences: UserPreferences) => {
    setPreferences(newPreferences)
    // Automatically get new recommendations if a movie is already selected
    if (selectedMovie) {
      setLoading(true)
      try {
        const result = await getRecommendations({
          movie_title: selectedMovie.title,
          user_preferences: newPreferences,
          num_recommendations: 5
        })
        setRecommendation(result)
      } catch (err) {
        console.error('Error getting recommendations:', err)
        setError('Failed to get recommendations')
      } finally {
        setLoading(false)
      }
    }
  }

  const handleSearchByPreferences = async () => {
    setIsSearchingByPreferences(true)
    setError(null)
    setPreferenceSearchResults([])
    
    try {
      const results = await searchMoviesByPreferences({
        favorite_genres: preferences.favorite_genres,
        min_rating: preferences.min_rating,
        preferred_decade: preferences.preferred_decade,
        limit: 20
      })
      setPreferenceSearchResults(results)
      
      if (results.length === 0) {
        setError('No movies found matching your preferences. Try adjusting your filters.')
      }
    } catch (err) {
      console.error('Error searching by preferences:', err)
      setError('Failed to search movies')
    } finally {
      setIsSearchingByPreferences(false)
    }
  }

  const handleLatestMovieClick = (movie: any) => {
    setSelectedLatestMovie(movie)
  }

  const learnFromUserInteraction = async (movie: any) => {
    if (!user) return
    
    try {
      // Extract genres from the movie user clicked
      const movieGenres = movie.genres.split(', ').map((g: string) => g.trim())
      
      // Update user preferences based on interaction
      const updatedPreferences = { ...preferences }
      
      // Add new genres to favorites if not already there
      movieGenres.forEach((genre: string) => {
        if (!updatedPreferences.favorite_genres.includes(genre)) {
          updatedPreferences.favorite_genres.push(genre)
        }
      })
      
      // Adjust rating preference based on movie rating
      if (movie.rating > updatedPreferences.min_rating) {
        updatedPreferences.min_rating = Math.max(
          updatedPreferences.min_rating - 0.2, 
          movie.rating - 1.0
        )
      }
      
      // Update decade preference towards the movie's decade
      const movieDecade = Math.floor(movie.year / 10) * 10
      updatedPreferences.preferred_decade = Math.round(
        (updatedPreferences.preferred_decade + movieDecade) / 2
      )
      
      setPreferences(updatedPreferences)
      
      // Save learned preferences
      localStorage.setItem(`preferences_${user.uid}`, JSON.stringify(updatedPreferences))
      
      // Get new recommendations based on clicked movie
      const result = await getRecommendations({
        movie_title: movie.title,
        user_preferences: updatedPreferences,
        num_recommendations: 5
      })
      setRecommendation(result)
      
    } catch (err) {
      console.error('Error learning from interaction:', err)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        {/* Show personalized recommendations only in Search & Recommend tab */}
        {recommendedMovies.length > 0 && activeTab === 'search' && (
          <div className="mb-8 bg-gradient-to-r from-purple-500/20 to-blue-500/20 backdrop-blur-md rounded-2xl p-6 border border-purple-500/30">
            <h2 className="text-3xl font-bold text-white mb-4 flex items-center">
              <span className="mr-3">✨</span>
              Your Personalized Recommendations
            </h2>
            <p className="text-gray-300 mb-6">
              Based on your favorite movies, here are {recommendedMovies.length} films we think you'll love!
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {recommendedMovies.map((movie) => (
                <div
                  key={movie.id}
                  onClick={() => setSelectedMovie(movie)}
                  className="bg-white/10 backdrop-blur-sm rounded-lg p-4 hover:bg-white/20 transition-all cursor-pointer border border-white/10 hover:border-purple-500/50"
                >
                  <h3 className="text-white font-bold text-lg mb-2">{movie.title}</h3>
                  <p className="text-gray-300 text-sm mb-2 line-clamp-2">{movie.description}</p>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">{movie.year}</span>
                    <span className="text-yellow-400">⭐ {movie.rating}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        <div className="flex space-x-4 mb-8">
          <button
            onClick={() => setActiveTab('latest')}
            className={`px-6 py-3 rounded-xl font-semibold transition-all ${
              activeTab === 'latest'
                ? 'bg-blue-500 text-white shadow-lg'
                : 'bg-white/10 text-gray-300 hover:bg-white/20'
            }`}
          >
            🎬 Latest Movies
          </button>
          <button
            onClick={() => {
              setActiveTab('search')
              if (movies.length === 0) loadMovies()
            }}
            className={`px-6 py-3 rounded-xl font-semibold transition-all ${
              activeTab === 'search'
                ? 'bg-blue-500 text-white shadow-lg'
                : 'bg-white/10 text-gray-300 hover:bg-white/20'
            }`}
          >
            🔍 Search & Recommend
          </button>
        </div>

        {activeTab === 'latest' && (
          <div className="space-y-6">
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-3xl font-bold text-white mb-2">
                    Latest Movies Worldwide
                  </h2>
                  <p className="text-gray-300">
                    From Hollywood, Bollywood, Tollywood, and more
                  </p>
                </div>
                <button
                  onClick={loadLatestMovies}
                  className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
                >
                  Refresh
                </button>
              </div>

              {error && (
                <div className="bg-red-500 text-white p-4 rounded-lg mb-6">
                  {error}
                </div>
              )}

              {loadingStates.latestMovies ? (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
                  <p className="text-white text-lg">Loading latest movies...</p>
                </div>
              ) : latestMovies.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-white text-lg">No movies available</p>
                </div>
              ) : (
                <MovieGrid
                  movies={latestMovies}
                  onMovieClick={handleLatestMovieClick}
                />
              )}
            </div>
          </div>
        )}

        {activeTab === 'search' && (
          <div className="space-y-8">
            {loadingStates.movies ? (
              <div className="bg-white/10 backdrop-blur-md rounded-xl p-12 text-center">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
                <p className="text-white text-lg">Loading movie database...</p>
              </div>
            ) : movies.length === 0 ? (
              <div className="bg-white/10 backdrop-blur-md rounded-xl p-12 text-center">
                <p className="text-white text-lg">No movies available</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Search Section */}
                <div className="space-y-6">
                  <MovieSearch
                    movies={movies}
                    onMovieSelect={handleMovieSelect}
                    selectedMovie={selectedMovie}
                  />
                  
                  <PreferencesForm
                    preferences={preferences}
                    onPreferencesChange={handlePreferencesChange}
                    onSearch={handleSearchByPreferences}
                    isSearching={isSearchingByPreferences}
                  />
                </div>

              {/* Recommendations Section */}
              <div className="space-y-6">
                {/* Show Preference Search Results */}
                {preferenceSearchResults.length > 0 && (
                  <div className="bg-white/10 backdrop-blur-md rounded-xl p-6">
                    <h3 className="text-xl font-bold text-white mb-4">
                      🎯 Movies Matching Your Preferences ({preferenceSearchResults.length})
                    </h3>
                    <div className="grid grid-cols-1 gap-3 max-h-[600px] overflow-y-auto">
                      {preferenceSearchResults.map((movie) => (
                        <div
                          key={movie.id}
                          onClick={() => handleMovieSelect(movie)}
                          className="bg-white/5 rounded-lg p-4 hover:bg-white/10 transition-all cursor-pointer border border-white/10 hover:border-blue-500/50"
                        >
                          <h4 className="text-white font-bold text-lg mb-2">{movie.title}</h4>
                          <p className="text-gray-300 text-sm mb-3 line-clamp-2">{movie.description}</p>
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-400">{movie.genres}</span>
                            <div className="flex items-center space-x-2">
                              <span className="text-gray-400">{movie.year}</span>
                              <span className="text-yellow-400">⭐ {movie.rating}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Show Selected Movie at the top */}
                {selectedMovie && (
                  <div className="bg-white/10 backdrop-blur-md rounded-xl p-6">
                    <h3 className="text-xl font-bold text-white mb-4">Selected Movie</h3>
                    <div className="bg-white/5 rounded-lg p-4">
                      <h4 className="text-white font-bold text-lg mb-2">{selectedMovie.title}</h4>
                      <p className="text-gray-300 text-sm mb-3">{selectedMovie.description}</p>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-400">{selectedMovie.genres}</span>
                        <div className="flex items-center space-x-2">
                          <span className="text-gray-400">{selectedMovie.year}</span>
                          <span className="text-yellow-400">⭐ {selectedMovie.rating}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {error && (
                  <div className="bg-red-500 text-white p-4 rounded-lg mb-6">
                    {error}
                  </div>
                )}

                {loading && (
                  <div className="flex items-center justify-center py-20">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white"></div>
                  </div>
                )}

                {!loading && recommendation && (
                  <RecommendationResult 
                    recommendation={recommendation} 
                    onMovieSelect={handleMovieSelect}
                  />
                )}

                {!loading && !recommendation && !error && (
                  <div className="bg-white/10 backdrop-blur-md rounded-xl p-12 text-center text-white">
                    <h2 className="text-2xl font-semibold mb-4">
                      Get Started
                    </h2>
                    <p className="text-gray-300">
                      Search for a movie and set your preferences to get personalized recommendations
                    </p>
                  </div>
                )}
              </div>
            </div>
            )}
          </div>
        )}
      </main>

      {selectedLatestMovie && (
        <MovieDetailModal
          movie={selectedLatestMovie}
          onClose={() => setSelectedLatestMovie(null)}
        />
      )}
    </div>
  )
}
