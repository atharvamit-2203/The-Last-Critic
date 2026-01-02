import os
import requests
from typing import Optional, List, Dict
from dotenv import load_dotenv
import time

load_dotenv()

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
        self.enabled = self.api_key is not None
        self.cache = {}
    
    def _call_gemini(self, prompt: str, max_tokens: int = 4000) -> str:
        cache_key = prompt + str(max_tokens)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            url = f"{self.base_url}?key={self.api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": 0.7
                }
            }
            
            response = requests.post(
                url,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['candidates'][0]['content']['parts'][0]['text'].strip()
                self.cache[cache_key] = content
                return content
            else:
                print(f"Gemini API error: {response.status_code} - {response.text}")
                return ""
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            return ""
    
    def generate_movie_database(self, count: int = 100) -> List[Dict]:
        if not self.enabled:
            return []
        
        try:
            prompt = f"""Generate {count} popular movies from all industries and time periods.

For EACH movie, provide in this EXACT format:

MOVIE 1:
Title: [Movie Title]
Year: [Release Year]
Rating: [6.0-9.5 based on actual ratings]
Industry: [Hollywood/Bollywood/Tollywood/Korean/etc]
Genres: [Genre1, Genre2, Genre3]
Description: [One sentence plot summary]
Month: [Release month 1-12]

Include movies from:
- Hollywood classics and modern hits
- Bollywood blockbusters
- Tollywood hits
- Korean cinema
- Japanese films
- Other international cinema

Generate exactly {count} movies."""
            
            response = self._call_gemini(prompt, max_tokens=4000)
            
            if response:
                return self._parse_movies(response)
            
        except Exception as e:
            print(f"Error generating movies: {e}")
        
        return []
    
    def _parse_movies(self, text: str) -> List[Dict]:
        movies = []
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
                        movie['release_month'] = int(value)
                    except:
                        movie['release_month'] = 6
            
            if 'title' in movie and 'description' in movie:
                movie.setdefault('genres', 'Drama')
                movie.setdefault('industry', 'International')
                movie.setdefault('rating', 7.0)
                movie.setdefault('year', 2020)
                movie.setdefault('release_month', 6)
                movies.append(movie)
        
        return movies