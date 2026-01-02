import os
import requests
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()

class XAIService:
    def __init__(self):
        self.api_key = os.getenv('XAI_API_KEY')
        self.base_url = "https://api.x.ai/v1/chat/completions"
        self.model = "grok-2-1212"
        self.enabled = self.api_key is not None
        self.cache = {}
    
    def _call_xai(self, messages: List[Dict], max_tokens: int = 1000) -> str:
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
                print(f"xAI API error: {response.status_code} - {response.text}")
                return ""
        except Exception as e:
            print(f"Error calling xAI: {e}")
            return ""
    
    def analyze_movie_reviews(self, movie_title: str, movie_year: str) -> Dict:
        """Analyze movie reviews using xAI Grok"""
        if not self.enabled:
            return {
                'movie_title': movie_title,
                'analysis': 'AI service not available. Please check configuration.',
                'error': 'Service unavailable'
            }
            
        try:
            prompt = f"""Analyze the movie "{movie_title}" ({movie_year}) by accessing your knowledge from:
- Critics reviews (Rotten Tomatoes, Metacritic, etc.)
- User reviews (IMDB, Letterboxd, etc.)
- YouTube reviews and reactions
- Social media sentiment
- Box office performance

Provide a comprehensive analysis with these sections:

OVERALL RECEPTION
[2-3 sentences summary]

MASS AUDIENCE APPEAL: [X/10]
★★★★★☆☆☆☆☆ ([X] stars)
Score and explanation - How mainstream audiences received it. Consider entertainment value, accessibility, star power, action, humor.

CLASS AUDIENCE APPEAL: [X/10]
★★★★★☆☆☆☆☆ ([X] stars)
Score and explanation - How critics and cinephiles view it. Consider direction, cinematography, performances, themes, artistic merit.

KEY STRENGTHS
- [Bullet points of major positives]

WEAKNESSES
- [Bullet points of criticisms]

TARGET DEMOGRAPHIC
Who will enjoy this most

FINAL VERDICT
Clear recommendation with reasoning

Be honest and balanced. Do NOT use ** for formatting. Use plain text for section headers."""

            messages = [
                {"role": "system", "content": "You are an expert film critic and analyst with comprehensive knowledge of cinema across all industries."},
                {"role": "user", "content": prompt}
            ]
            
            response = self._call_xai(messages, max_tokens=1200)
            
            if response:
                return {
                    'movie_title': movie_title,
                    'analysis': response,
                    'sources_analyzed': [
                        'Critics Reviews (Rotten Tomatoes, Metacritic)',
                        'User Reviews (IMDB, Letterboxd)',
                        'YouTube Reviews & Reactions',
                        'Social Media Sentiment',
                        'Box Office Performance'
                    ]
                }
            else:
                return {
                    'movie_title': movie_title,
                    'analysis': 'Unable to analyze movie. Please try again.',
                    'error': 'No response'
                }
            
        except Exception as e:
            print(f"Error analyzing movie: {e}")
            return {
                'movie_title': movie_title,
                'analysis': 'Unable to analyze movie at this time.',
                'error': str(e)
            }