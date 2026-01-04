import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Optional
import os

from models.movie import MovieResponse, RecommendationResponse
from services.ai_service import AIEnhancementService

class RecommendationEngine:
    def __init__(self):
        self.movies_df = None
        self.tfidf_matrix = None
        self.tfidf_vectorizer = None
        self.cosine_sim = None
        self.ai_service = AIEnhancementService()
        self.movie_db_service = None
    
    def load_data(self):
        """Load comprehensive movie dataset (3000 movies) for search and recommendations"""
        all_movies = []
        
        try:
            # Try TMDB first - NO DATE FILTER for comprehensive database
            from services.tmdb_database_service import TMDBDatabaseService
            tmdb_service = TMDBDatabaseService()
            
            if tmdb_service.enabled:
                print("🎬 Getting comprehensive movie database from TMDB...")
                tmdb_movies = tmdb_service.generate_comprehensive_database(3000)  # All movies
                if tmdb_movies:
                    all_movies.extend(tmdb_movies)
                    print(f"✅ TMDB: {len(tmdb_movies)} movies")
            
            # Add Groq movies for more variety
            from services.groq_service import GroqService
            groq_service = GroqService()
            
            if groq_service.enabled:
                print("🤖 Getting movies from Groq...")
                groq_movies = groq_service.generate_movie_database(3000)
                if groq_movies:
                    all_movies.extend(groq_movies)
                    print(f"✅ Groq: {len(groq_movies)} movies")
            
            # Deduplicate by title
            if all_movies:
                seen_titles = set()
                unique_movies = []
                for movie in all_movies:
                    title_key = movie['title'].lower().strip()
                    if title_key not in seen_titles:
                        seen_titles.add(title_key)
                        movie['id'] = len(unique_movies) + 1
                        unique_movies.append(movie)
                
                self.movies_df = pd.DataFrame(unique_movies)
                print(f"🎯 Total unique movies for search/recommendations: {len(self.movies_df)}")
                return
            
            # Fallback to sample if needed
            print("⚠️ No movies from APIs, using sample dataset")
            self.create_sample_dataset()
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            self.create_sample_dataset()
    
    def get_latest_movies(self, limit: int = 100) -> List[Dict]:
        """Get latest movies from last 30 days only (separate from main database)"""
        try:
            from services.tmdb_database_service import TMDBDatabaseService
            tmdb_service = TMDBDatabaseService()
            
            if tmdb_service.enabled:
                print(f"📅 Fetching latest movies from last 30 days...")
                # This will use date filtering
                latest_movies = tmdb_service.generate_latest_database(limit)
                print(f"✅ Found {len(latest_movies)} latest movies")
                return latest_movies
            else:
                print("❌ TMDB API not available for latest movies")
                return []
        except Exception as e:
            print(f"❌ Error fetching latest movies: {e}")
            return []
    
    def create_sample_dataset(self):
        """Create a sample movie dataset as fallback for search/recommendations"""
        sample_movies = [
            {"id": 1, "title": "Bang Bang", "genres": "Action, Thriller, Romance", "description": "A young bank receptionist gets entangled in the world of international espionage", "rating": 5.6, "year": 2014, "release_month": 10},
            {"id": 2, "title": "The Matrix", "genres": "Action, Sci-Fi", "description": "A computer hacker learns about the true nature of reality", "rating": 8.7, "year": 1999, "release_month": 3},
            {"id": 3, "title": "Inception", "genres": "Action, Sci-Fi, Thriller", "description": "A thief who steals corporate secrets through dream-sharing technology", "rating": 8.8, "year": 2010, "release_month": 7},
            {"id": 4, "title": "The Dark Knight", "genres": "Action, Crime, Drama", "description": "Batman faces the Joker in a battle for Gotham's soul", "rating": 9.0, "year": 2008, "release_month": 7},
            {"id": 5, "title": "3 Idiots", "genres": "Comedy, Drama", "description": "Two friends search for their long lost companion who inspired them to think differently", "rating": 8.4, "year": 2009, "release_month": 12},
        ]
        
        self.movies_df = pd.DataFrame(sample_movies)
        print(f"✓ Loaded {len(sample_movies)} sample movies for search/recommendations")
    
    def train_model(self):
        """Train the recommendation model using TF-IDF and cosine similarity"""
        if self.movies_df is None:
            raise Exception("Data not loaded. Call load_data() first.")
        
        # Create combined features for content-based filtering
        self.movies_df['combined_features'] = (
            self.movies_df['genres'].fillna('') + ' ' +
            self.movies_df['description'].fillna('') + ' ' +
            self.movies_df['title'].fillna('')
        )
        
        # Create TF-IDF matrix
        self.tfidf_vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000
        )
        
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(
            self.movies_df['combined_features']
        )
        
        # Calculate cosine similarity matrix
        self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
        
        print("Model trained successfully")
    
    def get_movie_index(self, title: str) -> Optional[int]:
        """Get the index of a movie by title"""
        matches = self.movies_df[
            self.movies_df['title'].str.lower() == title.lower()
        ]
        if len(matches) > 0:
            return matches.index[0]
        return None
    
    def get_all_movies(self, limit: int = 100, search: Optional[str] = None) -> List[MovieResponse]:
        """Get all movies without date filtering (for onboarding and search)"""
        if self.movies_df is None:
            return []

        filtered_df = self.movies_df.copy()

        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            search_condition = (
                filtered_df['title'].str.lower().str.contains(search_lower, na=False) |
                filtered_df['genres'].str.lower().str.contains(search_lower, na=False)
            )
            filtered_df = filtered_df.loc[search_condition]

        # Sort by rating (highest first)
        filtered_df = filtered_df.sort_values(by=['rating'], ascending=[False])

        movies = []
        for _, movie in filtered_df.head(limit).iterrows():
            movies.append(MovieResponse(
                id=int(movie['id']),
                title=movie['title'],
                genres=movie['genres'],
                description=movie['description'],
                rating=float(movie['rating']),
                year=int(movie['year']),
                release_month=int(movie['release_month']) if pd.notna(movie['release_month']) else None
            ))

        return movies

    def get_movies(self, limit: int = 100, search: Optional[str] = None) -> List[MovieResponse]:
        """Get all movies from comprehensive database (for search and recommendations)"""
        if self.movies_df is None or len(self.movies_df) == 0:
            return []

        df = self.movies_df.copy()

        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            search_condition = (
                df['title'].str.lower().str.contains(search_lower, na=False) |
                df['genres'].str.lower().str.contains(search_lower, na=False)
            )
            df = df.loc[search_condition]

        # Sort by popularity/rating
        df = df.sort_values(
            by=['rating', 'year'],
            ascending=[False, False]
        )

        movies = []
        for _, movie in df.head(limit).iterrows():
            movies.append(MovieResponse(
                id=int(movie['id']),
                title=movie['title'],
                genres=movie['genres'],
                description=movie['description'],
                rating=float(movie['rating']),
                year=int(movie['year']),
                release_month=int(movie['release_month']) if pd.notna(movie['release_month']) else None
            ))

        return movies
    
    def search_by_preferences(
        self,
        favorite_genres: List[str],
        min_rating: float,
        preferred_decade: int,
        limit: int = 20
    ) -> List[Dict]:
        """Search movies that match user preferences with flexible matching"""
        if self.movies_df is None:
            return []
        
        filtered_df = self.movies_df.copy()
        
        # Start with genre filtering if specified
        if favorite_genres:
            genre_pattern = '|'.join(favorite_genres)
            genre_matches = filtered_df[
                filtered_df['genres'].str.contains(genre_pattern, case=False, na=False)
            ]
            
            # If we have genre matches, use them
            if len(genre_matches) > 0:
                filtered_df = genre_matches
            else:
                # If no exact genre matches, be more flexible
                print(f"No exact matches for {favorite_genres}, showing related movies")
        
        # Apply rating filter with flexibility
        exact_rating_matches = filtered_df[filtered_df['rating'] >= min_rating]
        if len(exact_rating_matches) >= 5:
            filtered_df = exact_rating_matches
        else:
            # If too few high-rated matches, lower the threshold slightly
            relaxed_rating = max(min_rating - 1.0, 5.0)
            filtered_df = filtered_df[filtered_df['rating'] >= relaxed_rating]
            print(f"Relaxed rating from {min_rating} to {relaxed_rating} for more results")
        
        # Apply decade filter with flexibility
        decade_start = preferred_decade - 5
        decade_end = preferred_decade + 14
        decade_matches = filtered_df[
            (filtered_df['year'] >= decade_start) & (filtered_df['year'] <= decade_end)
        ]
        
        if len(decade_matches) >= 3:
            filtered_df = decade_matches
        else:
            # If too few decade matches, expand the range
            expanded_start = preferred_decade - 15
            expanded_end = preferred_decade + 25
            filtered_df = filtered_df[
                (filtered_df['year'] >= expanded_start) & (filtered_df['year'] <= expanded_end)
            ]
            print(f"Expanded decade range for more results")
        
        # Sort by rating (highest first) and then by year (newest first)
        filtered_df = filtered_df.sort_values(
            by=['rating', 'year'], 
            ascending=[False, False]
        )
        
        movies = []
        for _, movie in filtered_df.head(limit).iterrows():
            movies.append({
                'id': int(movie['id']),
                'title': movie['title'],
                'genres': movie['genres'],
                'description': movie['description'],
                'rating': float(movie['rating']),
                'year': int(movie['year']),
                'release_month': int(movie['release_month']) if pd.notna(movie['release_month']) else None,
                'mass_rating': round(float(movie['rating']) * 0.9, 1),
                'cinephile_rating': round(min(float(movie['rating']) * 1.1, 9.0), 1)
            })
        
        return movies
    
    def get_movie_by_id(self, movie_id: int) -> Optional[MovieResponse]:
        """Get a specific movie by ID"""
        if self.movies_df is None:
            return None

        matches = self.movies_df[self.movies_df['id'] == movie_id]
        if len(matches) > 0:
            movie = matches.iloc[0]
            return MovieResponse(
                id=int(movie['id']),
                title=movie['title'],
                genres=movie['genres'],
                description=movie['description'],
                rating=float(movie['rating']),
                year=int(movie['year']),
                release_month=int(movie['release_month']) if pd.notna(movie['release_month']) else None
            )
        return None
    
    def recommend(
        self,
        movie_title: str,
        user_preferences: Dict,
        num_recommendations: int = 5
    ) -> RecommendationResponse:
        """
        Generate recommendations based on movie title and user preferences
        """
        movie_idx = self.get_movie_index(movie_title)
        
        if movie_idx is None:
            return RecommendationResponse(
                should_watch=False,
                confidence=0.0,
                reason=f"Movie '{movie_title}' not found in database",
                recommended_movies=[],
                target_movie=None
            )
        
        # Get the target movie details
        target_movie = self.movies_df.iloc[movie_idx]
        
        # Get similarity scores
        sim_scores = list(enumerate(self.cosine_sim[movie_idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get recommended movie indices (deduplicated by movie ID and title)
        recommended_movies = []
        seen_ids = {int(target_movie['id'])}  # Track seen IDs, exclude target movie
        seen_titles = {target_movie['title'].lower().strip()}  # Track seen titles
        
        for idx, score in sim_scores[1:]:  # Skip first item (the movie itself)
            if len(recommended_movies) >= num_recommendations:
                break
                
            movie = self.movies_df.iloc[idx]
            movie_id = int(movie['id'])
            movie_title = movie['title'].lower().strip()
            
            # Skip if we've already added this movie by ID or title
            if movie_id in seen_ids or movie_title in seen_titles:
                continue
                
            seen_ids.add(movie_id)
            seen_titles.add(movie_title)
            
            # Generate reason for this recommendation
            reason = self._generate_recommendation_reason(
                target_movie=target_movie,
                recommended_movie=movie,
                similarity_score=score
            )
            
            recommended_movies.append(MovieResponse(
                id=movie_id,
                title=movie['title'],
                genres=movie['genres'],
                description=movie['description'],
                rating=float(movie['rating']),
                year=int(movie['year']),
                release_month=int(movie['release_month']) if pd.notna(movie['release_month']) else None,
                reason=reason,
                similarity_score=float(score)
            ))
        
        # Determine if user should watch based on preferences
        should_watch, confidence, reason = self._analyze_preferences(
            target_movie,
            user_preferences
        )
        # Enhance reason with AI if available
        if self.ai_service.enabled:
            reason = self.ai_service.enhance_recommendation_reason(
                movie_title=target_movie['title'],
                genres=target_movie['genres'],
                rating=float(target_movie['rating']),
                user_preferences=user_preferences,
                base_reason=reason
            )
        
        
        return RecommendationResponse(
            should_watch=should_watch,
            confidence=confidence,
            reason=reason,
            recommended_movies=recommended_movies,
            target_movie=MovieResponse(
                id=int(target_movie['id']),
                title=target_movie['title'],
                genres=target_movie['genres'],
                description=target_movie['description'],
                rating=float(target_movie['rating']),
                year=int(target_movie['year']),
                release_month=int(target_movie['release_month']) if pd.notna(target_movie['release_month']) else None
            )
        )
    
    def _analyze_preferences(
        self,
        movie: pd.Series,
        preferences: Dict
    ) -> tuple:
        """Analyze if movie matches user preferences"""
        score = 0
        max_score = 0
        reasons = []
        
        # Check genre preferences (weighted lower)
        if 'favorite_genres' in preferences and preferences['favorite_genres']:
            max_score += 30
            movie_genres = set(movie['genres'].lower().split(', '))
            user_genres = set(g.lower() for g in preferences['favorite_genres'])
            genre_overlap = movie_genres.intersection(user_genres)
            
            if genre_overlap:
                genre_score = (len(genre_overlap) / len(user_genres)) * 30
                score += genre_score
                reasons.append(f"Matches your favorite genres: {', '.join(genre_overlap)}")
            else:
                # Still give some points for quality movies even if genre doesn't match
                if movie['rating'] >= 8.0:
                    score += 10  # Partial credit for high-quality films
                    reasons.append(f"Highly rated {movie['genres']} film")
                else:
                    reasons.append(f"{movie['genres']} - different from your usual preferences")
        
        # Check minimum rating preference (most important)
        if 'min_rating' in preferences:
            max_score += 50  # Increased weight for quality
            min_rating = preferences['min_rating']
            if movie['rating'] >= min_rating:
                # Give full points if it meets the rating
                score += 50
                if movie['rating'] >= 8.0:
                    reasons.append(f"Excellent rating: {movie['rating']}/10")
                else:
                    reasons.append(f"Good rating: {movie['rating']}/10")
            else:
                # Partial credit if close to minimum
                rating_gap = min_rating - movie['rating']
                if rating_gap <= 1.0:
                    score += 25
                    reasons.append(f"Rating {movie['rating']}/10 is close to your preference")
                else:
                    reasons.append(f"Rating {movie['rating']}/10 is below your minimum")
        
        # Check year preference (weighted lower)
        if 'preferred_decade' in preferences:
            max_score += 20
            preferred_decade = preferences['preferred_decade']
            movie_decade = (movie['year'] // 10) * 10
            year_diff = abs(movie['year'] - preferred_decade)
            
            if movie_decade == preferred_decade:
                score += 20
                reasons.append(f"From your preferred decade: {preferred_decade}s")
            elif year_diff <= 10:
                # Give partial credit for adjacent decades
                score += 10
                reasons.append(f"From {movie_decade}s (close to {preferred_decade}s)")
        
        # Calculate confidence
        confidence = (score / max_score * 100) if max_score > 0 else 50
        
        # Adjusted threshold: 50% or above is worth watching
        should_watch = confidence >= 50
        
        reason = " | ".join(reasons) if reasons else "Based on content similarity"
        
        return should_watch, round(confidence, 2), reason
    
    def _generate_recommendation_reason(
        self,
        target_movie: pd.Series,
        recommended_movie: pd.Series,
        similarity_score: float
    ) -> str:
        """Generate a personalized reason for why this movie was recommended"""
        reasons = []
        
        # Genre overlap
        target_genres = set(target_movie['genres'].lower().split(', '))
        recommended_genres = set(recommended_movie['genres'].lower().split(', '))
        common_genres = target_genres & recommended_genres
        
        if common_genres:
            genre_list = ', '.join(sorted(common_genres))
            reasons.append(f"Shares {genre_list} genre{' ' if len(common_genres) == 1 else 's'}")
        
        # Similar rating
        rating_diff = abs(float(target_movie['rating']) - float(recommended_movie['rating']))
        if rating_diff < 0.5:
            reasons.append(f"Similar rating ({float(recommended_movie['rating'])}/10)")
        
        # Same era
        target_decade = (int(target_movie['year']) // 10) * 10
        recommended_decade = (int(recommended_movie['year']) // 10) * 10
        if target_decade == recommended_decade:
            reasons.append(f"From the same era ({recommended_decade}s)")
        
        # High similarity
        if similarity_score > 0.7:
            reasons.append("Very similar content and themes")
        elif similarity_score > 0.5:
            reasons.append("Similar storyline and style")
        
        if reasons:
            return " • ".join(reasons)
        else:
            return "Recommended based on content similarity"
    


    def _generate_movie_database(self) -> List[Dict]:
        """Generate comprehensive movie database using AI"""
        if not self.movie_db_service or not self.movie_db_service.enabled:
            return []
            
        try:
            prompt = """Generate a comprehensive movie database with 100+ popular movies from all industries and time periods (excluding December 2025).

Include movies from:
- Hollywood classics and modern hits
- Bollywood blockbusters
- Tollywood hits
- Korean cinema
- Japanese films
- Other international cinema

For EACH movie, provide in this EXACT format:

MOVIE 1:
Title: [Movie Title]
Year: [Release Year - NOT 2025 December]
Rating: [6.0-9.5 based on actual ratings]
Industry: [Hollywood/Bollywood/Tollywood/Korean/etc]
Genres: [Genre1, Genre2, Genre3]
Description: [One sentence plot summary]
Month: [Release month 1-12, avoid December if 2025]

Include popular movies like:
- Bang Bang (Bollywood action)
- The Matrix, Inception, Avengers series
- Baahubali, RRR, KGF
- Parasite, Oldboy
- Your Name, Spirited Away
- And many more across all genres and years

Generate at least 100 movies to ensure comprehensive search results."""

            messages = [
                {"role": "system", "content": "You are a comprehensive movie database expert with knowledge of global cinema across all time periods and industries."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.movie_db_service._call_llama(messages, max_tokens=4000, temperature=0.5)
            
            if response:
                return self._parse_movie_database(response)
            
        except Exception as e:
            print(f"Error generating movie database: {e}")
        
        return []

    def _parse_movie_database(self, text: str) -> List[Dict]:
        """Parse AI-generated movie database"""
        movies = []
        
        try:
            movie_blocks = text.split('MOVIE ')
            
            for block in movie_blocks[1:]:
                lines = block.strip().split('\n')
                movie = {'id': len(movies) + 1}
                
                for line in lines:
                    line = line.strip()
                    if ':' not in line:
                        continue
                    
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if key == 'title':
                        movie['title'] = value
                    elif key == 'year':
                        try:
                            movie['year'] = int(value)
                        except:
                            movie['year'] = 2020
                    elif key == 'rating':
                        try:
                            movie['rating'] = float(value)
                        except:
                            movie['rating'] = 7.0
                    elif key == 'industry':
                        movie['industry'] = value
                    elif key == 'genres':
                        movie['genres'] = value
                    elif key == 'description':
                        movie['description'] = value
                    elif key == 'month':
                        try:
                            month = int(value)
                            # Avoid December 2025 releases
                            if movie.get('year') == 2025 and month == 12:
                                month = 11
                            movie['release_month'] = month
                        except:
                            movie['release_month'] = 6
                
                if 'title' in movie and 'description' in movie:
                    movie.setdefault('genres', 'Drama')
                    movie.setdefault('industry', 'International')
                    movie.setdefault('rating', 7.0)
                    movie.setdefault('year', 2020)
                    movie.setdefault('release_month', 6)
                    movies.append(movie)
            
        except Exception as e:
            print(f"Error parsing movie database: {e}")
        
        return movies
