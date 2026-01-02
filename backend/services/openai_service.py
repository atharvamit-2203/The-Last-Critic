import os
import requests
from typing import Optional, List, Dict
from dotenv import load_dotenv
import time

load_dotenv()

class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-3.5-turbo"
        self.enabled = self.api_key is not None
        self.cache = {}
    
    def _call_openai(self, messages: List[Dict], max_tokens: int = 500, temperature: float = 0.7) -> str:
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
            else:
                print(f"OpenAI API error: {response.status_code} - {response.text}")
                return ""
        except Exception as e:
            print(f"Error calling OpenAI: {e}")
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

            messages = [
                {"role": "system", "content": "You are a comprehensive movie database expert."},
                {"role": "user", "content": prompt}
            ]
            
            response = self._call_openai(messages, max_tokens=4000, temperature=0.5)
            
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