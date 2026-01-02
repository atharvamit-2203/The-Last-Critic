import os
import requests
from typing import Optional, List, Dict
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

class AIEnhancementService:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "meta-llama/llama-3.2-3b-instruct:free"
        self.enabled = self.api_key is not None
        self.cache = {}
    
    def _call_llama(self, messages: List[Dict], max_tokens: int = 500, temperature: float = 0.7, retries: int = 3) -> str:
        """Call Llama model via OpenRouter with retry logic"""
        cache_key = str(messages) + str(max_tokens)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        for attempt in range(retries):
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "Movie Recommendation System"
                }
                
                payload = {
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
                
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content'].strip()
                    self.cache[cache_key] = content
                    return content
                elif response.status_code == 429:
                    wait_time = (attempt + 1) * 2
                    print(f"Rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"API error: {response.status_code} - {response.text}")
                    return ""
            except Exception as e:
                print(f"Error calling Llama: {e}")
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                return ""
        return ""
    
    def enhance_recommendation_reason(
        self,
        movie_title: str,
        genres: str,
        rating: float,
        user_preferences: dict,
        base_reason: str
    ) -> str:
        """
        Use Llama to generate a more engaging recommendation explanation
        """
        if not self.enabled:
            return base_reason
        
        try:
            prompt = f"""You are a movie recommendation expert. A user is considering watching "{movie_title}".

Movie Details:
- Genres: {genres}
- Rating: {rating}/10

User Preferences:
- Favorite Genres: {', '.join(user_preferences.get('favorite_genres', []))}
- Minimum Rating: {user_preferences.get('min_rating', 'Not specified')}
- Preferred Decade: {user_preferences.get('preferred_decade', 'Not specified')}s

Current Analysis: {base_reason}

Provide a brief, engaging 2-3 sentence recommendation explanation that's personalized and enthusiastic. Be conversational and helpful."""

            messages = [
                {"role": "system", "content": "You are a helpful movie recommendation assistant."},
                {"role": "user", "content": prompt}
            ]
            
            response = self._call_llama(messages, max_tokens=150, temperature=0.7)
            return response if response else base_reason
        
        except Exception as e:
            print(f"AI enhancement error: {e}")
            return base_reason
    
    def generate_movie_suggestions(self, user_preferences: dict, count: int = 10) -> List[Dict]:
        """
        Generate new movie suggestions based on user preferences using Llama
        """
        if not self.enabled:
            return []
        
        try:
            genres = ', '.join(user_preferences.get('favorite_genres', ['Action', 'Drama']))
            min_rating = user_preferences.get('min_rating', 7.0)
            decade = user_preferences.get('preferred_decade', 2000)
            
            prompt = f"""Generate {count} movie recommendations based on these preferences:
- Favorite Genres: {genres}
- Minimum Rating: {min_rating}/10
- Preferred Decade: {decade}s

For each movie, provide in this exact format:
Title: [Movie Title]
Genres: [Genre1, Genre2]
Year: [Year]
Rating: [X.X]
Description: [Brief one-sentence description]

---

Provide diverse, well-known movies that match these preferences."""

            messages = [
                {"role": "system", "content": "You are a movie database expert. Provide accurate movie information."},
                {"role": "user", "content": prompt}
            ]
            
            response = self._call_llama(messages, max_tokens=800, temperature=0.7)
            
            # Parse the response into structured movie data
            movies = self._parse_movie_suggestions(response)
            return movies
        
        except Exception as e:
            print(f"Movie generation error: {e}")
            return []
    
    def _parse_movie_suggestions(self, text: str) -> List[Dict]:
        """Parse Llama response into structured movie data"""
        movies = []
        movie_blocks = text.split('---')
        
        for block in movie_blocks:
            if not block.strip():
                continue
                
            movie = {}
            lines = block.strip().split('\n')
            
            for line in lines:
                if line.startswith('Title:'):
                    movie['title'] = line.replace('Title:', '').strip()
                elif line.startswith('Genres:'):
                    movie['genres'] = line.replace('Genres:', '').strip()
                elif line.startswith('Year:'):
                    try:
                        movie['year'] = int(line.replace('Year:', '').strip())
                    except:
                        movie['year'] = 2000
                elif line.startswith('Rating:'):
                    try:
                        movie['rating'] = float(line.replace('Rating:', '').strip())
                    except:
                        movie['rating'] = 7.0
                elif line.startswith('Description:'):
                    movie['description'] = line.replace('Description:', '').strip()
            
            if 'title' in movie and len(movie) >= 4:
                movies.append(movie)
        
        return movies
    
    def generate_movie_insights(self, movie_title: str, description: str) -> Optional[str]:
        """
        Generate interesting insights about a movie using Llama
        """
        if not self.enabled:
            return None
        
        try:
            prompt = f"""Provide a brief, interesting insight about the movie "{movie_title}".

Description: {description}

Give one compelling reason why someone might enjoy this movie (1-2 sentences)."""

            messages = [
                {"role": "system", "content": "You are a movie expert providing insights."},
                {"role": "user", "content": prompt}
            ]
            
            response = self._call_llama(messages, max_tokens=100, temperature=0.7)
            return response if response else None
        
        except Exception as e:
            print(f"AI insights error: {e}")
            return None
    
    def search_movie_by_title(self, movie_title: str) -> List:
        """
        Search for any movie by title using AI - returns movie details
        """
        if not self.enabled:
            return []
        
        try:
            from models.movie import MovieResponse
            from datetime import datetime
            
            current_year = datetime.now().year
            current_month = datetime.now().month
            
            prompt = f"""Search for the movie "{movie_title}" and provide its details.

If this movie exists, provide in this EXACT format:

Title: [Exact movie title]
Year: [Release year]
Genres: [Genre1, Genre2, Genre3]
Rating: [IMDB rating like 8.5, or 0.0 if not yet released or not available]
Description: [Brief one-sentence plot summary]

IMPORTANT: 
- Only include the movie if it was released BEFORE {current_year}-{current_month:02d} (before current month)
- If the movie is from current month or future, return: "NOT_FOUND"
- If the movie doesn't exist, return: "NOT_FOUND"
- Be accurate with the release year and rating"""

            messages = [
                {"role": "system", "content": "You are a movie database expert with comprehensive knowledge of all films."},
                {"role": "user", "content": prompt}
            ]
            
            response = self._call_llama(messages, max_tokens=300, temperature=0.3)
            
            if not response or "NOT_FOUND" in response:
                return []
            
            # Parse the response
            lines = response.strip().split('\n')
            movie_data = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if 'title' in key:
                        movie_data['title'] = value
                    elif 'year' in key:
                        try:
                            movie_data['year'] = int(value)
                        except:
                            movie_data['year'] = 2020
                    elif 'genre' in key:
                        movie_data['genres'] = value
                    elif 'rating' in key:
                        try:
                            movie_data['rating'] = float(value)
                        except:
                            movie_data['rating'] = 7.0
                    elif 'description' in key:
                        movie_data['description'] = value
            
            # Create MovieResponse if we have required fields
            if 'title' in movie_data and 'year' in movie_data:
                return [MovieResponse(
                    id=9999,  # AI-generated ID
                    title=movie_data.get('title', movie_title),
                    genres=movie_data.get('genres', 'Drama'),
                    description=movie_data.get('description', 'A compelling story'),
                    rating=movie_data.get('rating', 7.0),
                    year=movie_data.get('year', 2020)
                )]
            
            return []
            
        except Exception as e:
            print(f"Movie search error: {e}")
            return []

    
    def enhance_recommendation_reason(
        self,
        movie_title: str,
        genres: str,
        rating: float,
        user_preferences: dict,
        base_reason: str
    ) -> str:
        """
        Use OpenAI to generate a more engaging recommendation explanation
        """
        if not self.enabled:
            return base_reason
        
        try:
            prompt = f"""You are a movie recommendation expert. A user is considering watching "{movie_title}".

Movie Details:
- Genres: {genres}
- Rating: {rating}/10

User Preferences:
- Favorite Genres: {', '.join(user_preferences.get('favorite_genres', []))}
- Minimum Rating: {user_preferences.get('min_rating', 'Not specified')}
- Preferred Decade: {user_preferences.get('preferred_decade', 'Not specified')}s

Current Analysis: {base_reason}

Provide a brief, engaging 2-3 sentence recommendation explanation that's personalized and enthusiastic. Be conversational and helpful."""

            messages = [
                {"role": "system", "content": "You are a helpful movie recommendation assistant."},
                {"role": "user", "content": prompt}
            ]
            
            response = self._call_llama(messages, max_tokens=150, temperature=0.7)
            return response if response else base_reason
        
        except Exception as e:
            print(f"AI enhancement error: {e}")
            return base_reason
    
    def generate_movie_suggestions(self, user_preferences: dict, count: int = 10) -> List[Dict]:
        """
        Generate new movie suggestions based on user preferences using OpenAI
        """
        if not self.enabled:
            return []
        
        try:
            genres = ', '.join(user_preferences.get('favorite_genres', ['Action', 'Drama']))
            min_rating = user_preferences.get('min_rating', 7.0)
            decade = user_preferences.get('preferred_decade', 2000)
            
            prompt = f"""Generate {count} movie recommendations based on these preferences:
- Favorite Genres: {genres}
- Minimum Rating: {min_rating}/10
- Preferred Decade: {decade}s

For each movie, provide in this exact format:
Title: [Movie Title]
Genres: [Genre1, Genre2]
Year: [Year]
Rating: [X.X]
Description: [Brief one-sentence description]

---

Provide diverse, well-known movies that match these preferences."""

            messages = [
                {"role": "system", "content": "You are a movie database expert. Provide accurate movie information."},
                {"role": "user", "content": prompt}
            ]
            
            response = self._call_llama(messages, max_tokens=800, temperature=0.7)
            
            # Parse the response into structured movie data
            movies = self._parse_movie_suggestions(response) if response else []
            return movies
        
        except Exception as e:
            print(f"Movie generation error: {e}")
            return []
    
    def _parse_movie_suggestions(self, text: str) -> List[Dict]:
        """Parse OpenAI response into structured movie data"""
        movies = []
        movie_blocks = text.split('---')
        
        for block in movie_blocks:
            if not block.strip():
                continue
                
            movie = {}
            lines = block.strip().split('\n')
            
            for line in lines:
                if line.startswith('Title:'):
                    movie['title'] = line.replace('Title:', '').strip()
                elif line.startswith('Genres:'):
                    movie['genres'] = line.replace('Genres:', '').strip()
                elif line.startswith('Year:'):
                    try:
                        movie['year'] = int(line.replace('Year:', '').strip())
                    except:
                        movie['year'] = 2000
                elif line.startswith('Rating:'):
                    try:
                        movie['rating'] = float(line.replace('Rating:', '').strip())
                    except:
                        movie['rating'] = 7.0
                elif line.startswith('Description:'):
                    movie['description'] = line.replace('Description:', '').strip()
            
            if 'title' in movie and len(movie) >= 4:
                movies.append(movie)
        
        return movies
    
    def generate_movie_insights(self, movie_title: str, description: str) -> Optional[str]:
        """
        Generate interesting insights about a movie using OpenAI
        """
        if not self.enabled:
            return None
        
        try:
            prompt = f"""Provide a brief, interesting insight about the movie "{movie_title}".

Description: {description}

Give one compelling reason why someone might enjoy this movie (1-2 sentences)."""

            messages = [
                {"role": "system", "content": "You are a movie expert providing insights."},
                {"role": "user", "content": prompt}
            ]
            
            response = self._call_llama(messages, max_tokens=100, temperature=0.7)
            return response if response else None
        
        except Exception as e:
            print(f"AI insights error: {e}")
            return None
