import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv
from datetime import datetime
import time

load_dotenv()

class MovieDatabaseService:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.tmdb_api_key = "07a033cd0f89f2c4078903dd3913fb08"
        self.tmdb_base_url = "https://api.themoviedb.org/3"
        
        # Check if Ollama should be used
        self.use_ollama = os.getenv('USE_OLLAMA', 'false').lower() == 'true'
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        
        # OpenRouter settings
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "meta-llama/llama-3.2-3b-instruct:free"
        
        self.enabled = self.use_ollama or self.api_key is not None
        self.cache = {}  # Simple cache to avoid repeated API calls
        self.last_request_time = 0
        self.min_request_interval = 1 if self.use_ollama else 5  # Faster for local Ollama
    
    def _call_llama(self, messages: List[Dict], max_tokens: int = 1000, temperature: float = 0.7, retries: int = 2) -> str:
        """Call Llama model via Ollama (local) or OpenRouter with improved rate limiting"""
        # Create cache key from messages
        cache_key = str(messages) + str(max_tokens)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Try Ollama first if enabled
        if self.use_ollama:
            try:
                return self._call_ollama(messages, max_tokens, temperature)
            except Exception as e:
                print(f"Ollama failed: {e}, falling back to OpenRouter")
        
        # Fallback to OpenRouter or if Ollama not enabled
        if not self.api_key:
            return ""
        
        # Rate limiting - ensure minimum interval between requests
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            print(f"Rate limiting: waiting {sleep_time:.1f}s...")
            time.sleep(sleep_time)
        
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
                
                self.last_request_time = time.time()
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=20
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content'].strip()
                    self.cache[cache_key] = content
                    return content
                elif response.status_code == 429:
                    wait_time = (attempt + 1) * 5
                    print(f"Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{retries}...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"API error: {response.status_code} - {response.text}")
                    return ""
            except Exception as e:
                print(f"Error calling Llama (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(3)
                    continue
                return ""
        
        print("Max retries reached. Using fallback.")
        return ""
    
    def _call_ollama(self, messages: List[Dict], max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Call local Ollama API"""
        try:
            # Convert messages to Ollama format
            prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            print(f"Calling Ollama with model: {self.ollama_model}")
            
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload,
                timeout=120  # Increased timeout for longer responses
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('response', '').strip()
                if content:
                    print(f"✓ Ollama response received ({len(content)} chars)")
                    # Cache successful response
                    cache_key = str(messages) + str(max_tokens)
                    self.cache[cache_key] = content
                    return content
                else:
                    print("✗ Ollama returned empty response")
            else:
                print(f"✗ Ollama API error: {response.status_code} - {response.text}")
                return ""
        except requests.exceptions.Timeout:
            print(f"✗ Ollama request timed out")
            raise
        except Exception as e:
            print(f"✗ Error calling Ollama: {type(e).__name__}: {e}")
            raise
    
    def get_latest_movies(self, region: str = None, page: int = 1) -> List[Dict]:
        """Get movies released within the last 30 days from current date"""
        from datetime import datetime, timedelta
        
        all_movies = []
        seen_ids = set()
        
        # Calculate 30-day window
        current_date = datetime.now()
        thirty_days_ago = current_date - timedelta(days=30)
        
        # Fetch from ALL major film industries worldwide - maximum counts
        regions_to_fetch = [
            ('IN', 50),  # India (Hindi, Telugu, Tamil, Malayalam, Kannada)
            ('US', 30),  # Hollywood
            ('KR', 15),  # Korean
            ('JP', 10),  # Japanese
            ('CN', 10),  # Chinese
            ('FR', 8),   # French
            ('DE', 8),   # German
            ('ES', 8),   # Spanish
            ('IT', 5),   # Italian
            ('RU', 5),   # Russian
            ('TH', 5),   # Thai
            ('TR', 5),   # Turkish
            ('BR', 5),   # Brazilian
        ]
        
        for region_code, count in regions_to_fetch:
            try:
                movies = self._get_tmdb_latest_movies_filtered(region_code, page, thirty_days_ago, current_date)
                for movie in movies[:count]:
                    movie_id = movie['id']
                    movie_title = movie['title'].lower().strip()
                    
                    # Check for both ID and title duplicates
                    if movie_id not in seen_ids and not any(m['title'].lower().strip() == movie_title for m in all_movies):
                        seen_ids.add(movie_id)
                        all_movies.append(movie)
            except Exception as e:
                print(f"Error fetching from {region_code}: {e}")
                continue
        
        # If we don't have enough movies from TMDB, return what we have
        # Don't use fallback since those movies have already been released
        return all_movies[:200]  # Increase limit to show up to 200 movies
    
    def _get_tmdb_latest_movies_filtered(self, region: str = None, page: int = 1, start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """Get movies from TMDB within specific date range (last 30 days)"""
        for attempt in range(3):
            try:
                # Format dates for TMDB API
                start_date_str = start_date.strftime('%Y-%m-%d')
                end_date_str = end_date.strftime('%Y-%m-%d')
                
                # Use discover endpoint to get movies within date range
                discover_url = f"{self.tmdb_base_url}/discover/movie"
                params = {
                    'api_key': self.tmdb_api_key,
                    'language': 'en-US',
                    'page': page,
                    'region': region or 'US',
                    'sort_by': 'popularity.desc',
                    'primary_release_date.gte': start_date_str,
                    'primary_release_date.lte': end_date_str,
                    'vote_count.gte': 0
                }
                
                session = requests.Session()
                session.headers.update({
                    'User-Agent': 'MovieRecommendationApp/1.0',
                    'Accept': 'application/json'
                })
                
                # Try multiple pages to get more movies
                movies = []
                for page_num in [1, 2, 3, 4, 5]:  # Fetch 5 pages per region
                    params['page'] = page_num
                    response = session.get(discover_url, params=params, timeout=(5, 15))
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        for movie in data.get('results', []):
                            # Detect industry based on original language
                            original_language = movie.get('original_language', 'en')
                            industry = self._detect_industry(original_language)
                            
                            movies.append({
                                'id': movie.get('id'),
                                'title': movie.get('title', 'Unknown'),
                                'original_title': movie.get('original_title', movie.get('title', 'Unknown')),
                                'description': movie.get('overview', 'No description available'),
                                'rating': round(movie.get('vote_average', 0), 1),
                                'year': movie.get('release_date', end_date.strftime('%Y-%m-%d'))[:4] if movie.get('release_date') else str(end_date.year),
                                'genres': self._get_genre_names(movie.get('genre_ids', [])),
                                'industry': industry,
                                'popularity': int(movie.get('popularity', 1000)),
                                'poster_url': f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else None,
                                'backdrop_url': f"https://image.tmdb.org/t/p/w1280{movie.get('backdrop_path')}" if movie.get('backdrop_path') else None
                            })
                    
                    if len(movies) >= 100:  # Stop if we have enough
                        break
                    
                    if movies:
                        print(f"✓ Fetched {len(movies)} movies from {start_date_str} to {end_date_str}")
                        return movies
                
            except Exception as e:
                print(f"✗ TMDB attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    time.sleep(1 * (attempt + 1))
                    continue
        
        return []
    
    def _detect_industry(self, original_language: str) -> str:
        """Detect movie industry based on language"""
        industry_map = {
            'hi': 'Bollywood',
            'te': 'Tollywood', 
            'ta': 'Kollywood',
            'ml': 'Mollywood',
            'kn': 'Sandalwood',
            'bn': 'Bengali Cinema',
            'mr': 'Marathi Cinema',
            'gu': 'Gujarati Cinema',
            'pa': 'Punjabi Cinema',
            'or': 'Odia Cinema',
            'as': 'Assamese Cinema',
            'ko': 'Korean Cinema',
            'ja': 'Japanese Cinema',
            'zh': 'Chinese Cinema',
            'th': 'Thai Cinema',
            'vi': 'Vietnamese Cinema',
            'id': 'Indonesian Cinema',
            'ms': 'Malaysian Cinema',
            'tl': 'Filipino Cinema',
            'es': 'Spanish Cinema',
            'fr': 'French Cinema',
            'de': 'German Cinema',
            'it': 'Italian Cinema',
            'pt': 'Portuguese Cinema',
            'ru': 'Russian Cinema',
            'ar': 'Arabic Cinema',
            'tr': 'Turkish Cinema',
            'fa': 'Persian Cinema'
        }
        return industry_map.get(original_language, 'Hollywood')
    
    def _get_recent_fallback(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Fallback movies for recent releases within the last 30 days (Dec 2025 - Jan 2026)"""
        return [
            {"id": 4001, "title": "Dhurandhar", "description": "A gripping drama about human relationships and moral choices", "rating": 7.8, "year": "2025", "genres": "Drama, Thriller", "industry": "Bollywood", "popularity": 8500},
            {"id": 4002, "title": "Avatar: Fire and Ash", "description": "Jake Sully and his family face new threats on Pandora", "rating": 8.2, "year": "2025", "genres": "Sci-Fi, Adventure", "industry": "Hollywood", "popularity": 9500},
            {"id": 4003, "title": "The Batman Part II", "description": "Batman continues his war on crime in Gotham City", "rating": 8.0, "year": "2025", "genres": "Action, Crime", "industry": "Hollywood", "popularity": 9200},
            {"id": 4004, "title": "Fantastic Four", "description": "Marvel's first family joins the MCU", "rating": 7.5, "year": "2025", "genres": "Action, Sci-Fi", "industry": "Hollywood", "popularity": 8800},
            {"id": 4005, "title": "Blade Runner 2099", "description": "The future of humanity hangs in the balance", "rating": 8.1, "year": "2025", "genres": "Sci-Fi, Thriller", "industry": "Hollywood", "popularity": 8600},
            {"id": 4006, "title": "Salaar Part 2", "description": "The saga of Deva continues with more action and drama", "rating": 8.3, "year": "2025", "genres": "Action, Drama", "industry": "Tollywood", "popularity": 8900},
            {"id": 4007, "title": "Bade Miyan Chote Miyan 2", "description": "The duo returns for another action-packed adventure", "rating": 6.9, "year": "2025", "genres": "Action, Comedy", "industry": "Bollywood", "popularity": 7800},
            {"id": 4008, "title": "Thalapathy 69", "description": "Vijay's final film before entering politics", "rating": 8.4, "year": "2025", "genres": "Action, Drama", "industry": "Kollywood", "popularity": 9100},
            {"id": 4009, "title": "Squid Game: The Movie", "description": "The deadly games come to the big screen", "rating": 8.2, "year": "2025", "genres": "Thriller, Drama", "industry": "Korean Cinema", "popularity": 9300},
            {"id": 4010, "title": "Your Name 2", "description": "A new story of connection across time and space", "rating": 8.0, "year": "2025", "genres": "Animation, Romance", "industry": "Japanese Cinema", "popularity": 8400}
        ]
        """Get latest movies from TMDB API - December 2025 releases"""
        for attempt in range(3):
            try:
                from datetime import datetime, timedelta
                current_date = datetime.now()
                
                # Get movies specifically from December 2025
                start_date = '2025-12-01'
                end_date = '2025-12-31'
                
                # Use discover endpoint to get December 2025 movies
                discover_url = f"{self.tmdb_base_url}/discover/movie"
                params = {
                    'api_key': self.tmdb_api_key,
                    'language': 'en-US',
                    'page': page,
                    'region': region or 'US',
                    'sort_by': 'popularity.desc',  # Sort by popularity to get known movies
                    'primary_release_date.gte': start_date,
                    'primary_release_date.lte': end_date,
                    'vote_count.gte': 0  # No minimum to get all December releases
                }
                
                # Add session with retry and better timeout handling
                session = requests.Session()
                session.headers.update({
                    'User-Agent': 'MovieRecommendationApp/1.0',
                    'Accept': 'application/json'
                })
                
                response = session.get(
                    discover_url, 
                    params=params, 
                    timeout=(5, 15),  # (connect timeout, read timeout)
                )
                
                if response.status_code == 200:
                    data = response.json()
                    movies = []
                    
                    for movie in data.get('results', [])[:25]:
                        # Detect industry based on original language
                        original_language = movie.get('original_language', 'en')
                        industry = 'Hollywood'  # Default
                        
                        if original_language == 'hi':
                            industry = 'Bollywood'
                        elif original_language == 'te':
                            industry = 'Tollywood'
                        elif original_language == 'ta':
                            industry = 'Kollywood'
                        elif original_language == 'ml':
                            industry = 'Mollywood'
                        elif original_language == 'kn':
                            industry = 'Sandalwood'
                        elif original_language == 'ko':
                            industry = 'Korean'
                        elif original_language == 'ja':
                            industry = 'Japanese'
                        elif original_language == 'zh':
                            industry = 'Chinese'
                        elif original_language == 'es':
                            industry = 'Spanish'
                        elif original_language == 'fr':
                            industry = 'French'
                        
                        movies.append({
                            'id': movie.get('id'),
                            'title': movie.get('title', 'Unknown'),
                            'original_title': movie.get('original_title', movie.get('title', 'Unknown')),
                            'description': movie.get('overview', 'No description available'),
                            'rating': round(movie.get('vote_average', 0), 1),
                            'year': movie.get('release_date', current_date.strftime('%Y-%m-%d'))[:4] if movie.get('release_date') else str(current_date.year),
                            'genres': self._get_genre_names(movie.get('genre_ids', [])),
                            'industry': industry,
                            'popularity': int(movie.get('popularity', 1000)),
                            'poster_url': f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else None,
                            'backdrop_url': f"https://image.tmdb.org/t/p/w1280{movie.get('backdrop_path')}" if movie.get('backdrop_path') else None
                        })
                    
                    if movies:
                        print(f"✓ Successfully fetched {len(movies)} movies from TMDB")
                        return movies
                
                print(f"✗ TMDB API returned status {response.status_code}")
                
            except requests.exceptions.Timeout:
                print(f"✗ TMDB attempt {attempt + 1} timed out")
                if attempt < 2:
                    time.sleep(1 * (attempt + 1))  # Exponential backoff
                    continue
            except requests.exceptions.ConnectionError as e:
                print(f"✗ TMDB attempt {attempt + 1} connection error")
                if attempt < 2:
                    time.sleep(2 * (attempt + 1))  # Longer wait for connection issues
                    continue
            except Exception as e:
                print(f"✗ TMDB attempt {attempt + 1} failed: {type(e).__name__}")
                if attempt < 2:
                    time.sleep(1)
                    continue
        
        print("⚠ TMDB failed after all retries, using fallback movies")
        return self._get_december_2025_fallback()
    
    def _get_genre_names(self, genre_ids: List[int]) -> str:
        """Convert genre IDs to names"""
        genre_map = {
            28: 'Action', 12: 'Adventure', 16: 'Animation', 35: 'Comedy',
            80: 'Crime', 99: 'Documentary', 18: 'Drama', 10751: 'Family',
            14: 'Fantasy', 36: 'History', 27: 'Horror', 10402: 'Music',
            9648: 'Mystery', 10749: 'Romance', 878: 'Science Fiction',
            10770: 'TV Movie', 53: 'Thriller', 10752: 'War', 37: 'Western'
        }
        
        genres = [genre_map.get(gid, '') for gid in genre_ids[:3]]
        genres = [g for g in genres if g]  # Remove empty strings
        return ', '.join(genres) if genres else 'Drama'
    
    def analyze_movie_reviews(self, movie_title: str, movie_year: str) -> Dict:
        """Use Llama to analyze movie reviews from multiple sources"""
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
            
            response = self._call_llama(messages, max_tokens=1200, temperature=0.7)
            
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
    
    def _get_december_2025_fallback(self) -> List[Dict]:
        """Fallback December 2025 movies from all industries including recent regional releases"""
        return [
            # Latest Bollywood 2024-2025
            {"id": 1001, "title": "Pushpa 2: The Rule", "description": "Pushpa's power and influence grow as he continues his journey in the sandalwood smuggling world", "rating": 8.2, "year": "2024", "genres": "Action, Thriller", "industry": "Bollywood/Tollywood", "popularity": 9500, "poster_url": None, "backdrop_url": None},
            {"id": 1002, "title": "Stree 2", "description": "The mysterious woman returns with more supernatural adventures in Chanderi", "rating": 7.8, "year": "2024", "genres": "Horror, Comedy", "industry": "Bollywood", "popularity": 8900, "poster_url": None, "backdrop_url": None},
            {"id": 1003, "title": "Tu Meri Main Tera", "description": "A romantic comedy about misunderstandings and love", "rating": 6.8, "year": "2024", "genres": "Romance, Comedy", "industry": "Bollywood", "popularity": 7500, "poster_url": None, "backdrop_url": None},
            {"id": 1004, "title": "Kis Kisko Pyaar Karoon 2", "description": "Comedy of errors continues with multiple love interests", "rating": 6.5, "year": "2024", "genres": "Comedy, Romance", "industry": "Bollywood", "popularity": 7200, "poster_url": None, "backdrop_url": None},
            {"id": 1005, "title": "Jawan", "description": "A high-octane action thriller about a man seeking justice", "rating": 7.2, "year": "2023", "genres": "Action, Thriller", "industry": "Bollywood", "popularity": 8500, "poster_url": None, "backdrop_url": None},
            {"id": 1006, "title": "Pathaan", "description": "An exiled RAW agent partners with an ISI officer to take down a common enemy", "rating": 7.0, "year": "2023", "genres": "Action, Thriller", "industry": "Bollywood", "popularity": 8200, "poster_url": None, "backdrop_url": None},
            
            # Telugu (Tollywood)
            {"id": 1007, "title": "Salaar", "description": "A gang leader tries to keep a promise made to his dying friend", "rating": 7.5, "year": "2023", "genres": "Action, Drama", "industry": "Tollywood", "popularity": 8600, "poster_url": None, "backdrop_url": None},
            {"id": 1008, "title": "RRR", "description": "A fictitious story about two legendary freedom fighters", "rating": 7.9, "year": "2022", "genres": "Action, Drama", "industry": "Tollywood", "popularity": 9200, "poster_url": None, "backdrop_url": None},
            {"id": 1009, "title": "HanuMan", "description": "A man gains superpowers from Lord Hanuman", "rating": 7.6, "year": "2024", "genres": "Action, Fantasy", "industry": "Tollywood", "popularity": 7800, "poster_url": None, "backdrop_url": None},
            
            # Tamil (Kollywood)
            {"id": 1010, "title": "Leo", "description": "A mild-mannered man's past comes back to haunt him", "rating": 7.3, "year": "2023", "genres": "Action, Thriller", "industry": "Kollywood", "popularity": 8400, "poster_url": None, "backdrop_url": None},
            {"id": 1011, "title": "Jailer", "description": "A retired jailer seeks revenge for his son", "rating": 7.1, "year": "2023", "genres": "Action, Thriller", "industry": "Kollywood", "popularity": 8100, "poster_url": None, "backdrop_url": None},
            {"id": 1012, "title": "Vikram", "description": "A black ops agent tracks down a masked vigilante", "rating": 8.2, "year": "2022", "genres": "Action, Thriller", "industry": "Kollywood", "popularity": 8700, "poster_url": None, "backdrop_url": None},
            
            # Malayalam (Mollywood)
            {"id": 1013, "title": "2018", "description": "Stories of survival during the Kerala floods", "rating": 8.0, "year": "2023", "genres": "Drama, Thriller", "industry": "Mollywood", "popularity": 7600, "poster_url": None, "backdrop_url": None},
            {"id": 1014, "title": "Premalu", "description": "A romantic comedy about young love and life", "rating": 7.9, "year": "2024", "genres": "Romance, Comedy", "industry": "Mollywood", "popularity": 7400, "poster_url": None, "backdrop_url": None},
            {"id": 1015, "title": "Manjummel Boys", "description": "Friends on an adventure face unexpected danger", "rating": 8.3, "year": "2024", "genres": "Adventure, Thriller", "industry": "Mollywood", "popularity": 7900, "poster_url": None, "backdrop_url": None},
            
            # Kannada (Sandalwood)
            {"id": 1016, "title": "KGF Chapter 2", "description": "The blood-soaked land of Kolar Gold Fields has a new overlord", "rating": 8.4, "year": "2022", "genres": "Action, Drama", "industry": "Sandalwood", "popularity": 9000, "poster_url": None, "backdrop_url": None},
            {"id": 1017, "title": "Kantara", "description": "A tale of conflict between man and nature with divine intervention", "rating": 8.2, "year": "2022", "genres": "Action, Drama", "industry": "Sandalwood", "popularity": 8500, "poster_url": None, "backdrop_url": None},
            {"id": 1018, "title": "Ghost", "description": "A heist thriller with action-packed sequences", "rating": 7.0, "year": "2023", "genres": "Action, Thriller", "industry": "Sandalwood", "popularity": 7100, "poster_url": None, "backdrop_url": None},
            
            # Marathi
            {"id": 1019, "title": "Sairat", "description": "A young couple from different castes fall in love", "rating": 8.5, "year": "2016", "genres": "Romance, Drama", "industry": "Marathi", "popularity": 7000, "poster_url": None, "backdrop_url": None},
            {"id": 1020, "title": "Zombivli", "description": "A zombie outbreak in a Mumbai neighborhood", "rating": 7.2, "year": "2022", "genres": "Horror, Comedy", "industry": "Marathi", "popularity": 6800, "poster_url": None, "backdrop_url": None},
            
            # Bengali
            {"id": 1021, "title": "Aparajito", "description": "Coming of age story in rural Bengal", "rating": 8.1, "year": "2022", "genres": "Drama", "industry": "Bengali", "popularity": 6500, "poster_url": None, "backdrop_url": None},
            {"id": 1022, "title": "Pather Panchali", "description": "Classic tale of a family in rural Bengal", "rating": 8.4, "year": "1955", "genres": "Drama", "industry": "Bengali", "popularity": 7800, "poster_url": None, "backdrop_url": None},
            
            # Hollywood Recent
            {"id": 1017, "title": "Kantara", "description": "A Kambala champion faces off against an evil forest officer", "rating": 8.2, "year": "2022", "genres": "Action, Drama", "industry": "Sandalwood", "popularity": 8500, "poster_url": None, "backdrop_url": None},
            {"id": 1018, "title": "KGF Chapter 1", "description": "The journey of a young man from poverty to power", "rating": 8.2, "year": "2018", "genres": "Action, Drama", "industry": "Sandalwood", "popularity": 8600, "poster_url": None, "backdrop_url": None},
            
            # Hollywood Recent
            {"id": 1023, "title": "Oppenheimer", "description": "The story of J. Robert Oppenheimer and the atomic bomb", "rating": 8.4, "year": "2023", "genres": "Biography, Drama", "industry": "Hollywood", "popularity": 9100, "poster_url": None, "backdrop_url": None},
            {"id": 1024, "title": "Dune Part 2", "description": "Paul Atreides unites with Chani and the Fremen", "rating": 8.6, "year": "2024", "genres": "Sci-Fi, Adventure", "industry": "Hollywood", "popularity": 8900, "poster_url": None, "backdrop_url": None},
            {"id": 1025, "title": "Avengers: Endgame", "description": "The Avengers assemble one final time", "rating": 8.4, "year": "2019", "genres": "Action, Sci-Fi", "industry": "Hollywood", "popularity": 9500, "poster_url": None, "backdrop_url": None},
        ]
    
    def get_comprehensive_movies(self) -> List[Dict]:
        """Generate comprehensive movie database for search functionality"""
        if not self.enabled:
            return self._get_comprehensive_fallback()
            
        try:
            prompt = """Generate a comprehensive movie database with 200+ popular movies from ALL industries and time periods.

Include movies from:
- Hollywood (classics and modern): Matrix, Inception, Avengers, Dark Knight, Titanic, etc.
- Bollywood: Bang Bang, 3 Idiots, Dangal, Baahubali, RRR, KGF, Sholay, etc.
- Tollywood: Pushpa, Arjun Reddy, Magadheera, Eega, etc.
- Korean: Parasite, Oldboy, Train to Busan, Squid Game, etc.
- Japanese: Your Name, Spirited Away, Akira, etc.
- Other international cinema

For EACH movie, provide in this EXACT format:

MOVIE 1:
Title: [Movie Title]
Year: [Release Year]
Rating: [6.0-9.5 based on actual ratings]
Industry: [Hollywood/Bollywood/Tollywood/Korean/Japanese/etc]
Genres: [Genre1, Genre2, Genre3]
Description: [One sentence plot summary]
Month: [Release month 1-12]

Generate at least 200 movies across all decades (1970s-2024) and industries."""

            messages = [
                {"role": "system", "content": "You are a comprehensive movie database expert with knowledge of global cinema across all time periods and industries."},
                {"role": "user", "content": prompt}
            ]
            
            response = self._call_llama(messages, max_tokens=4000, temperature=0.5)
            
            if response:
                movies = self._parse_comprehensive_movies(response)
                if movies and len(movies) >= 50:
                    return movies
            
        except Exception as e:
            print(f"Error generating comprehensive movies: {e}")
        
        return self._get_comprehensive_fallback()
    
    def _parse_comprehensive_movies(self, text: str) -> List[Dict]:
        """Parse comprehensive AI movie database"""
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
            
        except Exception as e:
            print(f"Error parsing comprehensive movies: {e}")
        
        return movies
    
    def _get_comprehensive_fallback(self) -> List[Dict]:
        """Comprehensive fallback movie database from all industries"""
        return [
            # Bollywood
            {'id': 1, 'title': 'Bang Bang', 'genres': 'Action, Thriller, Romance', 'description': 'A young bank receptionist gets entangled in the world of international espionage', 'rating': 5.6, 'year': 2014, 'release_month': 10},
            {'id': 2, 'title': '3 Idiots', 'genres': 'Comedy, Drama', 'description': 'Two friends search for their long lost companion who inspired them to think differently', 'rating': 8.4, 'year': 2009, 'release_month': 12},
            {'id': 3, 'title': 'Dangal', 'genres': 'Biography, Drama, Sport', 'description': 'Former wrestler Mahavir Singh Phogat trains his daughters to become world-class wrestlers', 'rating': 8.4, 'year': 2016, 'release_month': 12},
            {'id': 4, 'title': 'Sholay', 'genres': 'Action, Adventure, Drama', 'description': 'Two criminals are hired to capture a ruthless dacoit who terrorizes the region', 'rating': 8.2, 'year': 1975, 'release_month': 8},
            {'id': 5, 'title': 'Zindagi Na Milegi Dobara', 'genres': 'Adventure, Comedy, Drama', 'description': 'Three friends on a bachelor trip discover themselves and their friendship', 'rating': 8.2, 'year': 2011, 'release_month': 7},
            
            # Hollywood
            {'id': 6, 'title': 'The Matrix', 'genres': 'Action, Sci-Fi', 'description': 'A computer hacker learns about the true nature of reality', 'rating': 8.7, 'year': 1999, 'release_month': 3},
            {'id': 7, 'title': 'Inception', 'genres': 'Action, Sci-Fi, Thriller', 'description': 'A thief who steals corporate secrets through dream-sharing technology', 'rating': 8.8, 'year': 2010, 'release_month': 7},
            {'id': 8, 'title': 'The Dark Knight', 'genres': 'Action, Crime, Drama', 'description': 'Batman faces the Joker in a battle for Gotham\'s soul', 'rating': 9.0, 'year': 2008, 'release_month': 7},
            {'id': 9, 'title': 'Avengers: Endgame', 'genres': 'Action, Adventure, Drama', 'description': 'The Avengers assemble once more to reverse Thanos\' actions', 'rating': 8.4, 'year': 2019, 'release_month': 4},
            {'id': 10, 'title': 'Titanic', 'genres': 'Drama, Romance', 'description': 'A seventeen-year-old aristocrat falls in love with a poor artist aboard the Titanic', 'rating': 7.9, 'year': 1997, 'release_month': 12},
            
            # Tollywood
            {'id': 11, 'title': 'Baahubali', 'genres': 'Action, Drama, Fantasy', 'description': 'A young man learns about his royal heritage and fights to reclaim his kingdom', 'rating': 8.0, 'year': 2015, 'release_month': 7},
            {'id': 12, 'title': 'RRR', 'genres': 'Action, Drama, History', 'description': 'A fictitious story about two legendary freedom fighters', 'rating': 7.9, 'year': 2022, 'release_month': 3},
            {'id': 13, 'title': 'Pushpa', 'genres': 'Action, Crime, Thriller', 'description': 'A laborer rises through the ranks of a red sandalwood smuggling syndicate', 'rating': 7.6, 'year': 2021, 'release_month': 12},
            {'id': 14, 'title': 'KGF', 'genres': 'Action, Crime, Drama', 'description': 'Rocky rises from poverty to become the king of a gold mine', 'rating': 8.2, 'year': 2018, 'release_month': 12},
            {'id': 15, 'title': 'Arjun Reddy', 'genres': 'Drama, Romance', 'description': 'A surgeon becomes self-destructive after his girlfriend marries someone else', 'rating': 8.1, 'year': 2017, 'release_month': 8},
            
            # Korean
            {'id': 16, 'title': 'Parasite', 'genres': 'Comedy, Drama, Thriller', 'description': 'A poor family schemes to become employed by a wealthy family', 'rating': 8.5, 'year': 2019, 'release_month': 5},
            {'id': 17, 'title': 'Oldboy', 'genres': 'Action, Drama, Mystery', 'description': 'A man seeks revenge after being imprisoned for 15 years without knowing why', 'rating': 8.4, 'year': 2003, 'release_month': 11},
            {'id': 18, 'title': 'Train to Busan', 'genres': 'Action, Horror, Thriller', 'description': 'Passengers fight for survival during a zombie outbreak on a train', 'rating': 7.6, 'year': 2016, 'release_month': 7},
            
            # Japanese
            {'id': 19, 'title': 'Your Name', 'genres': 'Animation, Drama, Romance', 'description': 'Two teenagers share a profound, magical connection upon discovering they are swapping bodies', 'rating': 8.2, 'year': 2016, 'release_month': 8},
            {'id': 20, 'title': 'Spirited Away', 'genres': 'Animation, Adventure, Family', 'description': 'A girl enters a world ruled by gods and witches where humans are changed into beasts', 'rating': 9.2, 'year': 2001, 'release_month': 7}
        ]