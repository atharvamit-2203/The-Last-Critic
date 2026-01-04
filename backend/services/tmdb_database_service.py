import os
import requests
from typing import List, Dict
import time
from datetime import datetime, timedelta

class TMDBDatabaseService:
    """Generate large movie database using TMDB API"""
    
    def __init__(self):
        self.api_key = os.getenv('TMDB_API_KEY')
        self.base_url = "https://api.themoviedb.org/3"
        self.enabled = bool(self.api_key)
        
        # Calculate date range: last 1 month from today
        today = datetime.now()
        one_month_ago = today - timedelta(days=30)
        self.release_date_gte = one_month_ago.strftime('%Y-%m-%d')
        self.release_date_lte = today.strftime('%Y-%m-%d')
        
        if not self.enabled:
            print("⚠ TMDB API key not found - database generation disabled")
        else:
            print(f"📅 Fetching movies from {self.release_date_gte} to {self.release_date_lte}")
    
    def generate_latest_database(self, target_count: int = 100) -> List[Dict]:
        """Generate latest movies from TMDB (last 30 days only)"""
        if not self.enabled:
            print("TMDB API not available")
            return []
        
        print(f"Starting TMDB latest movies generation (target: {target_count} movies from last 30 days)...")
        
        all_movies = []
        seen_ids = set()
        
        # First: Try to get movies using date filters
        print(f"📅 Date Range: {self.release_date_gte} to {self.release_date_lte}")
        print(f"🎬 Fetching latest movies from last 30 days...")
        
        # Strategy 1: Date-filtered movies by region
        date_strategies = [
            {'region': 'IN', 'language': 'hi', 'name': 'Bollywood', 'target': int(target_count * 0.20)},
            {'region': 'IN', 'language': 'te', 'name': 'Tollywood', 'target': int(target_count * 0.10)},
            {'region': 'IN', 'language': 'ta', 'name': 'Kollywood', 'target': int(target_count * 0.10)},
            {'region': 'US', 'language': 'en', 'name': 'Hollywood', 'target': int(target_count * 0.30)},
            {'region': 'KR', 'language': 'ko', 'name': 'Korean', 'target': int(target_count * 0.10)},
        ]
        
        # Fetch date-filtered movies
        all_movies.extend(self._fetch_parallel(date_strategies, use_date_filter=True, seen_ids=seen_ids))
        
        # Strategy 2: Now Playing & Popular (to catch very recent releases)
        print(f"\n🔥 Fetching now playing and popular movies...")
        now_playing = self._fetch_now_playing_and_popular(target_count // 3, seen_ids)
        all_movies.extend(now_playing)
        
        print(f"\n✓ Generated {len(all_movies)} latest movies from TMDB")
        return all_movies
    
    def generate_comprehensive_database(self, target_count: int = 3000) -> List[Dict]:
        """Generate comprehensive movie database from TMDB (all time, no date filter)"""
        if not self.enabled:
            print("TMDB API not available")
            return []
        
        print(f"Starting TMDB comprehensive database generation (target: {target_count} movies)...")
        
        all_movies = []
        seen_ids = set()
        
        # Define strategies for all-time comprehensive database
        strategies = [
            # Indian Cinema (60%)
            {'region': 'IN', 'language': 'hi', 'name': 'Bollywood', 'target': int(target_count * 0.25)},
            {'region': 'IN', 'language': 'te', 'name': 'Tollywood', 'target': int(target_count * 0.15)},
            {'region': 'IN', 'language': 'ta', 'name': 'Kollywood', 'target': int(target_count * 0.10)},
            {'region': 'IN', 'language': 'ml', 'name': 'Mollywood', 'target': int(target_count * 0.05)},
            {'region': 'IN', 'language': 'kn', 'name': 'Sandalwood', 'target': int(target_count * 0.03)},
            {'region': 'IN', 'language': 'bn', 'name': 'Bengali', 'target': int(target_count * 0.02)},
            # International (40%)
            {'region': 'US', 'language': 'en', 'name': 'Hollywood', 'target': int(target_count * 0.20)},
            {'region': 'KR', 'language': 'ko', 'name': 'Korean', 'target': int(target_count * 0.08)},
            {'region': 'JP', 'language': 'ja', 'name': 'Japanese', 'target': int(target_count * 0.05)},
            {'region': 'CN', 'language': 'zh', 'name': 'Chinese', 'target': int(target_count * 0.03)},
            {'region': 'FR', 'language': 'fr', 'name': 'French', 'target': int(target_count * 0.02)},
            {'region': 'ES', 'language': 'es', 'name': 'Spanish', 'target': int(target_count * 0.02)},
        ]
        
        print(f"🎬 Fetching comprehensive movie database (all time)...")
        
        # Use threading for parallel requests
        import threading
        import queue
        
        results_queue = queue.Queue()
        threads = []
        
        def fetch_worker(strategy):
            try:
                movies = self._fetch_movies_by_region(
                    region=strategy['region'],
                    language=strategy['language'],
                    industry=strategy['name'],
                    target=strategy['target'],
                    use_date_filter=False  # NO date filter for comprehensive database
                )
                results_queue.put((strategy['name'], movies))
            except Exception as e:
                print(f"Error fetching {strategy['name']}: {e}")
                results_queue.put((strategy['name'], []))
        
        # Start all threads
        for strategy in strategies:
            thread = threading.Thread(target=fetch_worker, args=(strategy,))
            thread.start()
            threads.append(thread)
        
        # Collect results as they complete
        completed = 0
        while completed < len(strategies):
            try:
                industry_name, movies = results_queue.get(timeout=60)
                completed += 1
                
                # Add unique movies
                added_count = 0
                for movie in movies:
                    if movie['id'] not in seen_ids:
                        seen_ids.add(movie['id'])
                        movie['id'] = len(all_movies) + 1
                        all_movies.append(movie)
                        added_count += 1
                
                print(f"✓ {industry_name}: {added_count} movies (Total: {len(all_movies)})")
                
            except queue.Empty:
                print("Timeout waiting for results")
                break
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=5)
        
        print(f"\n✓ Generated {len(all_movies)} unique movies from TMDB in parallel")
        return all_movies
    
    def _fetch_parallel(self, strategies: list, use_date_filter: bool, seen_ids: set) -> List[Dict]:
        """Fetch movies in parallel using threading"""
        import threading
        import queue
        
        results_queue = queue.Queue()
        threads = []
        movies_list = []
        
        def fetch_worker(strategy):
            try:
                movies = self._fetch_movies_by_region(
                    region=strategy['region'],
                    language=strategy['language'],
                    industry=strategy['name'],
                    target=strategy['target'],
                    use_date_filter=use_date_filter
                )
                results_queue.put((strategy['name'], movies))
            except Exception as e:
                print(f"Error fetching {strategy['name']}: {e}")
                results_queue.put((strategy['name'], []))
        
        for strategy in strategies:
            thread = threading.Thread(target=fetch_worker, args=(strategy,))
            thread.start()
            threads.append(thread)
        
        completed = 0
        while completed < len(strategies):
            try:
                industry_name, movies = results_queue.get(timeout=60)
                completed += 1
                
                added_count = 0
                for movie in movies:
                    if movie['id'] not in seen_ids:
                        seen_ids.add(movie['id'])
                        movies_list.append(movie)
                        added_count += 1
                
                print(f"✓ {industry_name}: {added_count} movies")
            except queue.Empty:
                break
        
        for thread in threads:
            thread.join(timeout=5)
        
        return movies_list
    
    def _fetch_now_playing_and_popular(self, target: int, seen_ids: set) -> List[Dict]:
        """Fetch now playing and popular movies to catch very recent releases"""
        movies = []
        
        endpoints = [
            ('movie/now_playing', 'Now Playing'),
            ('movie/popular', 'Popular'),
            ('trending/movie/week', 'Trending')
        ]
        
        for endpoint, name in endpoints:
            try:
                url = f"{self.base_url}/{endpoint}"
                params = {'api_key': self.api_key, 'page': 1}
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    
                    added = 0
                    for item in results:
                        if item['id'] not in seen_ids:
                            # Check if movie is recent (within 3 months)
                            release_date = item.get('release_date', '')
                            if release_date:
                                from datetime import datetime, timedelta
                                try:
                                    movie_date = datetime.strptime(release_date, '%Y-%m-%d')
                                    three_months_ago = datetime.now() - timedelta(days=90)
                                    
                                    if movie_date >= three_months_ago:
                                        movie = self._convert_tmdb_movie(item, 'Latest')
                                        if movie:
                                            seen_ids.add(item['id'])
                                            movies.append(movie)
                                            added += 1
                                            
                                            if len(movies) >= target:
                                                break
                                except:
                                    pass
                    
                    print(f"  {name}: {added} recent movies")
                    
                    if len(movies) >= target:
                        break
                        
            except Exception as e:
                print(f"  Error fetching {name}: {e}")
        
        return movies
    
    def _fetch_movies_by_region(self, region: str, language: str, industry: str, target: int, use_date_filter: bool = False) -> List[Dict]:
        """Fetch movies for specific region and language"""
        movies = []
        seen_tmdb_ids = set()
        pages_to_fetch = (target // 20) + 2  # TMDB returns ~20 per page
        
        for page in range(1, min(pages_to_fetch, 500)):  # TMDB limit
            try:
                # Discover movies with filters
                url = f"{self.base_url}/discover/movie"
                params = {
                    'api_key': self.api_key,
                    'region': region,
                    'with_original_language': language,
                    'sort_by': 'popularity.desc',
                    'page': page,
                    'vote_count.gte': 1 if use_date_filter else 10,  # Very low threshold for recent movies
                }
                
                # Add date filters only for latest movies
                if use_date_filter:
                    params['primary_release_date.gte'] = self.release_date_gte
                    params['primary_release_date.lte'] = self.release_date_lte
                
                response = requests.get(url, params=params, timeout=15)
                
                if response.status_code == 429:  # Rate limit
                    print(f"  Rate limited, waiting 2s...")
                    time.sleep(2)
                    continue
                elif response.status_code != 200:
                    print(f"  Error on page {page}: {response.status_code}")
                    if response.status_code in [500, 502, 503, 504]:  # Server errors
                        time.sleep(1)
                        continue
                    break
                
                data = response.json()
                results = data.get('results', [])
                
                if not results:
                    break
                
                for item in results:
                    tmdb_id = item.get('id')
                    if tmdb_id in seen_tmdb_ids:
                        continue
                    
                    seen_tmdb_ids.add(tmdb_id)
                    
                    # Convert TMDB format to our format
                    movie = self._convert_tmdb_movie(item, industry)
                    if movie:
                        movies.append(movie)
                    
                    if len(movies) >= target:
                        return movies
                
                # Rate limiting - faster for parallel requests
                time.sleep(0.3)  # 3 requests per second per thread
                
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                print(f"  Connection error on page {page}: {e}")
                time.sleep(2)  # Wait before retry
                continue
            except Exception as e:
                print(f"  Error fetching page {page}: {e}")
                break
        
        return movies
    
    def _convert_tmdb_movie(self, tmdb_data: Dict, industry: str) -> Dict:
        """Convert TMDB movie data to our format"""
        try:
            # Extract year from release_date
            release_date = tmdb_data.get('release_date', '')
            year = int(release_date.split('-')[0]) if release_date else 2020
            
            # Extract month
            month = 6
            if release_date and len(release_date.split('-')) >= 2:
                try:
                    month = int(release_date.split('-')[1])
                except:
                    pass
            
            # Map genre IDs to names
            genre_map = {
                28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy",
                80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family",
                14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music",
                9648: "Mystery", 10749: "Romance", 878: "Sci-Fi", 10770: "TV Movie",
                53: "Thriller", 10752: "War", 37: "Western"
            }
            
            genre_ids = tmdb_data.get('genre_ids', [])
            genres = [genre_map.get(gid, "Drama") for gid in genre_ids[:3]]
            genres_str = ", ".join(genres) if genres else "Drama"
            
            # Language mapping
            lang_map = {
                'hi': 'Hindi', 'te': 'Telugu', 'ta': 'Tamil', 
                'ml': 'Malayalam', 'kn': 'Kannada', 'en': 'English',
                'ko': 'Korean', 'ja': 'Japanese', 'es': 'Spanish',
                'fr': 'French', 'de': 'German', 'it': 'Italian'
            }
            original_lang = tmdb_data.get('original_language', 'en')
            language = lang_map.get(original_lang, original_lang.upper())
            
            # Get poster image URL
            poster_path = tmdb_data.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
            
            movie = {
                'id': tmdb_data.get('id'),
                'title': tmdb_data.get('title', 'Unknown'),
                'year': year,
                'genres': genres_str,
                'description': tmdb_data.get('overview', 'No description available'),
                'rating': round(tmdb_data.get('vote_average', 7.0), 1),
                'industry': industry,
                'release_month': month,
                'language': language,
                'poster_url': poster_url,
                'backdrop_path': tmdb_data.get('backdrop_path'),
            }
            
            return movie
            
        except Exception as e:
            print(f"  Error converting movie: {e}")
            return None
