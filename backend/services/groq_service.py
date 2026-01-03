import os
import requests
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()

class GroqService:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"
        self.enabled = self.api_key is not None
        self.cache = {}
    
    def _call_groq(self, messages: List[Dict], max_tokens: int = 4000) -> str:
        cache_key = str(messages) + str(max_tokens)
        if cache_key in self.cache:
            print("Using cached Groq response")
            return self.cache[cache_key]
        
        if not self.enabled:
            print("Groq service not enabled - missing API key")
            return ""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            print(f"Calling Groq API with model: {self.model}")
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"Groq API response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                print(f"Groq response length: {len(content)} characters")
                self.cache[cache_key] = content
                return content
            else:
                print(f"Groq API error: {response.status_code} - {response.text}")
                return ""
        except Exception as e:
            print(f"Error calling Groq: {e}")
            return ""
    
    def generate_movie_database(self, count: int = 100) -> List[Dict]:
        if not self.enabled:
            print("Groq service not enabled")
            return []
        
        print(f"🎬 Starting Groq movie generation for {count} movies...")
        
        # Start with smaller batch for testing
        batch_size = min(50, count)
        all_movies = []
        seen_titles = set()
        
        try:
            prompt = f"""Generate {batch_size} popular movies from different industries and time periods.

For EACH movie, provide in this EXACT format:

MOVIE 1:
Title: The Matrix
Year: 1999
Rating: 8.7
Industry: Hollywood
Genres: Action, Sci-Fi
Description: A computer hacker learns about the true nature of reality
Month: 3

MOVIE 2:
Title: 3 Idiots
Year: 2009
Rating: 8.4
Industry: Bollywood
Genres: Comedy, Drama
Description: Two friends search for their long lost companion
Month: 12

Include diverse movies from:
- Bollywood (Hindi cinema)
- Hollywood blockbusters
- Tollywood (Telugu cinema)
- Korean cinema
- Other international films

Generate exactly {batch_size} movies with this exact format. Each movie must have all 7 fields."""

            messages = [
                {"role": "system", "content": "You are a movie database expert. Generate movies in the exact format requested."},
                {"role": "user", "content": prompt}
            ]
            
            print("Calling Groq API...")
            response = self._call_groq(messages, max_tokens=6000)
            
            if response:
                print(f"✅ Got response from Groq ({len(response)} chars)")
                print(f"First 500 chars: {response[:500]}")
                
                movies = self._parse_movies(response)
                print(f"✅ Parsed {len(movies)} movies from Groq")
                return movies
            else:
                print("❌ No response from Groq")
                return []
                
        except Exception as e:
            print(f"❌ Error generating movies: {e}")
            return []
    def _parse_movies(self, text: str) -> List[Dict]:
        movies = []
        seen_titles = set()  # Track unique titles
        
        print(f"Parsing response... Total length: {len(text)} characters")
        
        movie_blocks = text.split('MOVIE ')
        print(f"Found {len(movie_blocks)} blocks (including header)")
        
        for block in movie_blocks[1:]:
            lines = block.strip().split('\n')
            movie = {}
            
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
                        movie['release_month'] = int(value)
                    except:
                        movie['release_month'] = 6
            
            if 'title' in movie and 'description' in movie:
                # Deduplicate by normalized title
                title_key = movie['title'].lower().strip()
                if title_key in seen_titles:
                    print(f"  - Skipping duplicate: {movie['title']}")
                    continue
                    
                seen_titles.add(title_key)
                movie['id'] = len(movies) + 1
                movie.setdefault('genres', 'Drama')
                movie.setdefault('industry', 'International')
                movie.setdefault('rating', 7.0)
                movie.setdefault('year', 2020)
                movie.setdefault('release_month', 6)
                movies.append(movie)
                print(f"  ✓ Added: {movie['title']} ({movie.get('year', 'N/A')})")
            else:
                missing = []
                if 'title' not in movie:
                    missing.append('title')
                if 'description' not in movie:
                    missing.append('description')
                print(f"  ✗ Incomplete movie (missing {', '.join(missing)}): {str(movie)[:100]}")
        
        print(f"✓ Parsed {len(movies)} unique movies from Groq response")
        return movies