import requests
from typing import Optional, List, Dict

class OllamaService:
    def __init__(self):
        self.base_url = "http://localhost:11434/api/generate"
        self.model = "llama3.2"
        self.enabled = True
        self.cache = {}
    
    def _call_ollama(self, prompt: str, max_tokens: int = 1000) -> str:
        cache_key = prompt + str(max_tokens)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7,
                    "num_ctx": 1024  # Very small context for max speed
                }
            }
            
            print(f"✓ Calling Ollama at {self.base_url} with model {self.model}")
            print(f"  Target: <60 seconds on CPU...")
            response = requests.post(
                self.base_url,
                json=payload,
                timeout=60  # 60 seconds max
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('response', '').strip()
                if content:
                    print(f"✓ Ollama response received ({len(content)} chars)")
                    self.cache[cache_key] = content
                    return content
                else:
                    print("✗ Ollama returned empty response")
                    return ""
            else:
                print(f"✗ Ollama API error: {response.status_code} - {response.text}")
                return ""
        except requests.exceptions.ConnectionError as e:
            print(f"✗ Connection Error: Ollama is not running at {self.base_url}")
            print("  → Please start Ollama: 'ollama serve'")
            self.enabled = False
            return ""
        except requests.exceptions.Timeout:
            print(f"✗ Timeout: Ollama took too long to respond")
            return ""
        except Exception as e:
            print(f"✗ Error calling Ollama: {type(e).__name__}: {e}")
            return ""
    
    def _gather_movie_ratings(self, movie_title: str, movie_year: str) -> str:
        """First step: Gather ratings and reception data from various sources"""
        # Check cache first
        cache_key = f"ratings_{movie_title}_{movie_year}"
        if cache_key in self.cache:
            print(f"✓ Using cached ratings data")
            return self.cache[cache_key]
        
        prompt = f"""For the movie "{movie_title}" ({movie_year}), provide ratings and reception data:

You MUST provide data even if you don't have specific information. Use reasonable estimates based on:
- The movie's title and themes
- Typical ratings for this genre/year
- Industry standards

1. IMDb Rating: [Provide estimated X/10]
2. Rotten Tomatoes: [Provide estimated critics % and audience %]
3. Metacritic: [Provide estimated score/100]
4. Google/YouTube Reception: [positive/mixed/negative based on title analysis]
5. Box Office: [estimated performance level]
6. Critical Consensus: [provide intelligent analysis based on genre]
7. Audience Response: [provide analysis based on themes]

Be confident and provide data. NO disclaimers about lacking information."""

        response = self._call_ollama(prompt, max_tokens=500)
        if response:
            cache_key = f"ratings_{movie_title}_{movie_year}"
            self.cache[cache_key] = response
        return response if response else "Limited data available."
    
    def analyze_movie_reviews(self, movie_title: str, movie_year: str) -> Dict:
        """Analyze movie reviews using local Ollama"""
        if not self.enabled:
            return {
                'movie_title': movie_title,
                'analysis': 'Ollama service not available.',
                'error': 'Service unavailable'
            }
            
        try:
            # Check if full analysis is cached
            analysis_cache_key = f"analysis_{movie_title}_{movie_year}"
            if analysis_cache_key in self.cache:
                print(f"✓ Using cached analysis for {movie_title}")
                return self.cache[analysis_cache_key]
            
            # SINGLE OPTIMIZED CALL - Gather + Analyze in one prompt
            print(f"🎬 Analyzing {movie_title} (optimized for speed)...")
            
            prompt = f"""Analyze "{movie_title}" ({movie_year}) quickly and effectively.

Provide concise analysis (plain text, NO asterisks):

OVERALL RECEPTION
[1-2 sentences on reception]

MASS AUDIENCE APPEAL: X/10
[1 detailed paragraph on mainstream appeal]

CLASS AUDIENCE APPEAL: X/10
[1 detailed paragraph on critical reception]

KEY STRENGTHS
- [3 bullet points]

WEAKNESSES
- [2 bullet points]

TARGET DEMOGRAPHIC
[1 sentence]

FINAL VERDICT
[1-2 sentences with clear recommendation]

Be specific and confident. Plain text only."""

            response = self._call_ollama(prompt, max_tokens=400)  # Reduced for speed
            
            if response and len(response.strip()) > 50:
                result = {
                    'movie_title': movie_title,
                    'analysis': response,
                    'sources_analyzed': [
                        'AI Film Analysis',
                        'Cinema Knowledge Base',
                        'Genre Patterns'
                    ]
                }
                # Cache the complete analysis
                self.cache[analysis_cache_key] = result
                return result
            else:
                error_msg = '''Unable to analyze movie. 

Please ensure:
1. Ollama is installed (https://ollama.com)
2. Ollama is running: open terminal and run "ollama serve"
3. Model is installed: run "ollama pull llama3.2"

Then refresh the page and try again.'''
                return {
                    'movie_title': movie_title,
                    'analysis': error_msg,
                    'error': 'Ollama not available'
                }
            
        except Exception as e:
            print(f"Error analyzing movie: {e}")
            return {
                'movie_title': movie_title,
                'analysis': 'Unable to analyze movie. Please ensure Ollama is running with llama3.2 model.',
                'error': str(e)
            }