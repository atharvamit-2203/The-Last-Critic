import os
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, Optional, List
from datetime import datetime
from pathlib import Path

class FirebaseService:
    def __init__(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            firebase_admin.get_app()
        except ValueError:
            # Initialize Firebase Admin SDK with service account
            # Look for service account file in parent directory (Movie Recommendation folder)
            service_account_path = Path(__file__).parent.parent.parent / "paisa-buddy-c7145-firebase-adminsdk-fbsvc-00cb318b79.json"
            
            if service_account_path.exists():
                cred = credentials.Certificate(str(service_account_path))
                firebase_admin.initialize_app(cred)
                print("Firebase initialized with service account key")
            else:
                # Fallback to alternative location
                service_account_path = Path(__file__).parent.parent / "firebase-admin-key.json"
                if service_account_path.exists():
                    cred = credentials.Certificate(str(service_account_path))
                    firebase_admin.initialize_app(cred)
                    print("Firebase initialized with service account key")
                else:
                    print("Warning: firebase service account key not found.")
                    print("Some features may be limited. Please generate service account key.")
                    # Initialize with project ID only (limited functionality)
                    try:
                        firebase_admin.initialize_app(options={
                            'projectId': 'paisa-buddy-c7145'
                        })
                    except Exception as e:
                        print(f"Error initializing Firebase: {e}")
                        raise
        
        self.db = firestore.client()
    
    def create_user(self, user_id: str, email: str, display_name: str, photo_url: Optional[str] = None) -> Dict:
        """Create or update user in Firestore"""
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_data = {
                'email': email,
                'displayName': display_name,
                'photoURL': photo_url,
                'createdAt': firestore.SERVER_TIMESTAMP,
                'lastLogin': firestore.SERVER_TIMESTAMP,
                'preferences': {
                    'favorite_genres': [],
                    'min_rating': 7.0,
                    'preferred_decade': 2000
                },
                'watchHistory': [],
                'favorites': []
            }
            user_ref.set(user_data, merge=True)
            return {'success': True, 'user_id': user_id}
        except Exception as e:
            print(f"Error creating user: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user data from Firestore"""
        try:
            user_ref = self.db.collection('users').document(user_id)
            doc = user_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def update_user_preferences(self, user_id: str, preferences: Dict) -> Dict:
        """Update user preferences"""
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_ref.update({
                'preferences': preferences,
                'updatedAt': firestore.SERVER_TIMESTAMP
            })
            return {'success': True}
        except Exception as e:
            print(f"Error updating preferences: {e}")
            return {'success': False, 'error': str(e)}
    
    def add_to_watch_history(self, user_id: str, movie_data: Dict) -> Dict:
        """Add movie to user's watch history"""
        try:
            user_ref = self.db.collection('users').document(user_id)
            watch_entry = {
                'movieId': movie_data.get('id'),
                'title': movie_data.get('title'),
                'watchedAt': firestore.SERVER_TIMESTAMP
            }
            user_ref.update({
                'watchHistory': firestore.ArrayUnion([watch_entry])
            })
            return {'success': True}
        except Exception as e:
            print(f"Error adding to watch history: {e}")
            return {'success': False, 'error': str(e)}
    
    def add_to_favorites(self, user_id: str, movie_id: str) -> Dict:
        """Add movie to user's favorites"""
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_ref.update({
                'favorites': firestore.ArrayUnion([movie_id])
            })
            return {'success': True}
        except Exception as e:
            print(f"Error adding to favorites: {e}")
            return {'success': False, 'error': str(e)}
    
    def remove_from_favorites(self, user_id: str, movie_id: str) -> Dict:
        """Remove movie from user's favorites"""
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_ref.update({
                'favorites': firestore.ArrayRemove([movie_id])
            })
            return {'success': True}
        except Exception as e:
            print(f"Error removing from favorites: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_user_favorites(self, user_id: str) -> List[str]:
        """Get user's favorite movie IDs"""
        try:
            user = self.get_user(user_id)
            if user:
                return user.get('favorites', [])
            return []
        except Exception as e:
            print(f"Error getting favorites: {e}")
            return []
    
    def add_recommendation(self, user_id: str, recommendation_data: Dict) -> Dict:
        """Add movie to user's recommendations (prevent duplicates)"""
        try:
            # Check if recommendation already exists
            existing_query = self.db.collection('recommendations').where(filter=firestore.FieldFilter('userId', '==', user_id)).where(filter=firestore.FieldFilter('movieId', '==', recommendation_data.get('movie_id')))
            existing_docs = list(existing_query.stream())
            
            if existing_docs:
                return {'success': True, 'message': 'Already recommended', 'recommendation_id': existing_docs[0].id}
            
            # Add new recommendation
            recommendation_ref = self.db.collection('recommendations').add({
                'userId': user_id,
                'movieId': recommendation_data.get('movie_id'),
                'movieTitle': recommendation_data.get('movie_title'),
                'movieGenres': recommendation_data.get('movie_genres'),
                'movieRating': recommendation_data.get('movie_rating'),
                'movieYear': recommendation_data.get('movie_year'),
                'movieDescription': recommendation_data.get('movie_description'),
                'source': recommendation_data.get('source', 'user_click'),
                'recommendedAt': firestore.SERVER_TIMESTAMP
            })
            return {'success': True, 'recommendation_id': recommendation_ref[1].id}
        except Exception as e:
            print(f"Error adding recommendation: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_user_recommendations(self, user_id: str) -> List[Dict]:
        """Get user's recommended movies"""
        try:
            recommendations_ref = self.db.collection('recommendations')
            query = recommendations_ref.where(filter=firestore.FieldFilter('userId', '==', user_id)).limit(50)
            docs = query.stream()
            
            recommendations = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                recommendations.append(data)
            
            # Sort by timestamp in Python instead of Firestore
            recommendations.sort(key=lambda x: x.get('recommendedAt', 0), reverse=True)
            return recommendations
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []
    
    def initialize_collections(self):
        """Initialize Firestore collections with sample structure"""
        try:
            # Create a sample user document to initialize the collection
            sample_user = {
                'email': 'sample@example.com',
                'displayName': 'Sample User',
                'photoURL': None,
                'createdAt': firestore.SERVER_TIMESTAMP,
                'lastLogin': firestore.SERVER_TIMESTAMP,
                'preferences': {
                    'favorite_genres': ['Action', 'Drama'],
                    'min_rating': 7.0,
                    'preferred_decade': 2020
                },
                'watchHistory': [],
                'favorites': []
            }
            self.db.collection('users').document('sample_user').set(sample_user)
            
            # Initialize recommendations collection
            sample_recommendation = {
                'userId': 'sample_user',
                'movieId': 1,
                'movieTitle': 'Sample Movie',
                'movieGenres': 'Action, Drama',
                'movieRating': 8.0,
                'movieYear': 2023,
                'movieDescription': 'Sample movie description',
                'source': 'user_click',
                'recommendedAt': firestore.SERVER_TIMESTAMP
            }
            self.db.collection('recommendations').add(sample_recommendation)
            print("Firestore collections initialized successfully")
            return {'success': True}
        except Exception as e:
            print(f"Error initializing collections: {e}")
            return {'success': False, 'error': str(e)}
