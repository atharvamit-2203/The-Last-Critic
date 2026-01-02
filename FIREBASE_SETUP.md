# Firebase Setup Instructions

## Steps to Complete Firebase Integration

### 1. Get Firebase Config for Frontend

1. Go to Firebase Console: https://console.firebase.google.com/project/paisa-buddy-c7145
2. Click on "Project Settings" (gear icon)
3. Scroll down to "Your apps" section
4. Click "Add app" or select existing web app
5. Copy the `firebaseConfig` object
6. Update `frontend/src/lib/firebase.ts` with your actual config values

The config should look like:
```javascript
const firebaseConfig = {
  apiKey: "YOUR_ACTUAL_API_KEY",
  authDomain: "paisa-buddy-c7145.firebaseapp.com",
  projectId: "paisa-buddy-c7145",
  storageBucket: "paisa-buddy-c7145.appspot.com",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID"
}
```

### 2. Get Firebase Admin SDK Service Account (Backend)

1. Go to Firebase Console: https://console.firebase.google.com/project/paisa-buddy-c7145/settings/serviceaccounts/adminsdk
2. Click "Generate new private key"
3. Save the JSON file as `firebase-admin-key.json` in the backend folder
4. Update `backend/services/firebase_service.py` to load this file

Replace the initialization code with:
```python
import os
from pathlib import Path

# Get the path to the service account key
service_account_path = Path(__file__).parent.parent / "firebase-admin-key.json"

if service_account_path.exists():
    cred = credentials.Certificate(str(service_account_path))
else:
    # Fallback to environment variable or project ID
    cred = credentials.ApplicationDefault()
    
firebase_admin.initialize_app(cred)
```

### 3. Enable Google Authentication

1. Go to Firebase Console: https://console.firebase.google.com/project/paisa-buddy-c7145/authentication/providers
2. Click on "Get Started" if not already enabled
3. Enable "Google" sign-in method
4. Add authorized domains: `localhost`, and your production domain

### 4. Firestore Database Structure

The app will create the following structure:

```
users (collection)
  └── {userId} (document)
      ├── email: string
      ├── displayName: string
      ├── photoURL: string
      ├── createdAt: timestamp
      ├── lastLogin: timestamp
      ├── preferences: object
      │   ├── favorite_genres: array
      │   ├── min_rating: number
      │   └── preferred_decade: number
      ├── watchHistory: array of objects
      │   └── {movieId, title, watchedAt}
      └── favorites: array of movie IDs
```

### 5. Security Rules (Optional)

Go to Firestore Rules and update:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

## Current Status

- ✅ Firebase packages installed
- ✅ Authentication components created
- ✅ Backend API endpoints for user management
- ⏳ Need to configure Firebase credentials
- ⏳ Need to enable Google Sign-in in Firebase Console

## Next Steps

1. Complete the Firebase configuration steps above
2. Restart the backend server
3. Refresh the frontend
4. Test Google Sign-in
