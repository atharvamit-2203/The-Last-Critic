import os
import requests
from typing import List, Dict
import time

class TMDBDatabaseService:
    """Generate large movie database using TMDB API"""
    
    def __init__(self):
        self.api_key = os.getenv('TMDB_API_KEY')
        self.base_url = "https://api.themoviedb.org/3"
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            print("⚠ TMDB API key not found - database generation disabled")
    
    def generate_movie_database(self, target_count: int = 1200) -> List[Dict]:
        """Generate comprehensive movie database from TMDB"""
        if not self.enabled:
            print("TMDB API not available")
            return []
        
        print(f"Starting TMDB database generation (target: {target_count} movies)...")
        
        all_movies = []
        seen_ids = set()
        
        # Define genres and regions for diverse coverage
        strategies = [
            # Indian Cinema
            {'region': 'IN', 'language': 'hi', 'name': 'Bollywood', 'target': int(target_count * 0.30)},
            {'region': 'IN', 'language': 'te', 'name': 'Tollywood', 'target': int(target_count * 0.20)},
            {'region': 'IN', 'language': 'ta', 'name': 'Kollywood', 'target': int(target_count * 0.15)},
            {'region': 'IN', 'language': 'ml', 'name': 'Mollywood', 'target': int(target_count * 0.10)},
            {'region': 'IN', 'language': 'kn', 'name': 'Sandalwood', 'target': int(target_count * 0.10)},
            # International
            {'region': 'US', 'language': 'en', 'name': 'Hollywood', 'target': int(target_count * 0.10)},
            {'region': 'KR', 'language': 'ko', 'name': 'Korean', 'target': int(target_count * 0.03)},
            {'region': 'JP', 'language': 'ja', 'name': 'Japanese', 'target': int(target_count * 0.02)},
        ]
        
        for strategy in strategies:
            print(f"\nFetching {strategy['name']} movies (target: {strategy['target']})...")
            movies = self._fetch_movies_by_region(
                region=strategy['region'],
                language=strategy['language'],
                industry=strategy['name'],
                target=strategy['target']
            )
            
            # Add unique movies
            for movie in movies:
                if movie['id'] not in seen_ids:
                    seen_ids.add(movie['id'])
                    movie['id'] = len(all_movies) + 1  # Reassign sequential ID
                    all_movies.append(movie)
            
            print(f"  ✓ Added {len(movies)} {strategy['name']} movies (Total: {len(all_movies)})")
            
            if len(all_movies) >= target_count:
                break
        
        print(f"\n✓ Generated {len(all_movies)} unique movies from TMDB")
        return all_movies
    
    def _fetch_movies_by_region(self, region: str, language: str, industry: str, target: int) -> List[Dict]:
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
                    'vote_count.gte': 10,  # Quality filter
                }
                
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
                
                # Rate limiting - slower to avoid connection issues
                time.sleep(0.5)  # 2 requests per second to avoid connection reset
                
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
            }
            
            return movie
            
        except Exception as e:
            print(f"  Error converting movie: {e}")
            return None
