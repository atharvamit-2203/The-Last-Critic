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
            return self.cache[cache_key]
        
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
            else:
                print(f"Groq API error: {response.status_code} - {response.text}")
                return ""
        except Exception as e:
            print(f"Error calling Groq: {e}")
            return ""
    
    def generate_movie_database(self, count: int = 100) -> List[Dict]:
        if not self.enabled:
            return []
        
        # Don't use cache for movie generation
        print(f"Starting generation of {count} movies...")
        
        # Generate in batches for better results
        batch_size = min(300, count)  # Generate up to 300 at a time
        all_movies = []
        seen_titles = set()
        
        # Calculate number of batches needed
        num_batches = (count + batch_size - 1) // batch_size
        
        for batch_num in range(num_batches):
            remaining = count - len(all_movies)
            current_batch_size = min(batch_size, remaining)
            
            if current_batch_size <= 0:
                break
                
            print(f"Generating batch {batch_num + 1}/{num_batches} ({current_batch_size} movies)...")
            
            try:
                prompt = f"""Generate {current_batch_size} UNIQUE popular and iconic movies from ALL film industries worldwide, with special focus on Indian cinema.

For EACH movie, provide in this EXACT format:

MOVIE 1:
Title: [Movie Title]
Year: [Release Year 1900-2025]
Rating: [5.0-9.5 based on actual ratings]
Industry: [Bollywood/Tollywood/Kollywood/Mollywood/Sandalwood/Hollywood/Korean/etc]
Genres: [Genre1, Genre2, Genre3]
Description: [One sentence plot summary]
Month: [Release month 1-12]

IMPORTANT - Include diverse representation:
- Bollywood (Hindi cinema): 30% - Include classics from 1950s to 2025
- Tollywood (Telugu cinema): 20% - Include from 1980s to 2025  
- Kollywood (Tamil cinema): 15% - Include from 1970s to 2025
- Mollywood (Malayalam cinema): 10% - Include quality films from all eras
- Sandalwood (Kannada cinema): 10% - Include notable films
- Hollywood: 10% - Major blockbusters and classics
- Other (Korean, Japanese, European, etc): 5%

Cover ALL decades from 1900 to 2025. Include:
- Legendary classics (1950s-1980s)
- Popular hits (1990s-2000s)  
- Modern blockbusters (2010s-2025)
- Recent releases (2023-2025)

Generate exactly {current_batch_size} UNIQUE movies with accurate real data. NO DUPLICATES."""

                messages = [
                    {"role": "system", "content": "You are a comprehensive movie database expert with knowledge of ALL world cinema."},
                    {"role": "user", "content": prompt}
                ]
                
                response = self._call_groq(messages, max_tokens=8000)  # Increased for more movies
                
                if response:
                    print(f"\n{'='*60}")
                    print(f"RAW GROQ RESPONSE (first 1000 chars):")
                    print(response[:1000])
                    print(f"{'='*60}\n")
                    
                    batch_movies = self._parse_movies(response)
                    
                    # Deduplicate across batches
                    for movie in batch_movies:
                        title_key = movie['title'].lower().strip()
                        if title_key not in seen_titles:
                            seen_titles.add(title_key)
                            movie['id'] = len(all_movies) + 1  # Reassign ID
                            all_movies.append(movie)
                            
                            if len(all_movies) >= count:
                                break
                    
                    print(f"✓ Total movies collected: {len(all_movies)}/{count}")
                    
            except Exception as e:
                print(f"Error generating batch: {e}")
                break
        
        print(f"✓ Generated {len(all_movies)} unique movies from Groq")
        return all_movies
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