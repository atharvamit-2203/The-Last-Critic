# The Last Critic - Quick Setup Guide

## 🚀 One-Click Setup (Windows)

1. **Download/Clone** this repository
2. **Double-click** `start-the-last-critic.bat`
3. **Wait** for both services to start (2-3 minutes)
4. **Open** http://localhost:3000 in your browser
5. **Enjoy** The Last Critic!

## 🔧 Manual Setup

### Prerequisites
- Python 3.8+ 
- Node.js 18+
- Git (optional)

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🎯 Features

✅ **AI-Powered Recommendations** - Content-based filtering with TF-IDF  
✅ **Smart Movie Search** - Find any movie in our database  
✅ **Preference Matching** - Personalized based on your taste  
✅ **Similar Movies** - Discover new films you'll love  
✅ **Latest Movies** - Stay updated with new releases  
✅ **User Authentication** - Google Sign-in support  
✅ **Responsive Design** - Works on all devices  

## 🌟 How It Works

1. **Sign In** with Google (optional but recommended)
2. **Complete Onboarding** - Select your favorite movies
3. **Search Movies** - Find films you're considering
4. **Get Recommendations** - AI analyzes and suggests
5. **Discover Similar** - Find movies you'll love

## 🔍 API Endpoints

- `GET /api/movies` - Get movie database
- `POST /api/recommend` - Get recommendations  
- `GET /api/latest-movies` - Latest releases
- `GET /health` - Health check
- `GET /docs` - API documentation

## 🎬 Movie Database

The Last Critic includes 250+ movies from:
- Hollywood blockbusters and classics
- Bollywood hits and critically acclaimed films  
- Tollywood (Telugu) cinema
- Kollywood (Tamil) movies
- Mollywood (Malayalam) films
- International cinema (Korean, Japanese, European)

## 🚨 Troubleshooting

**Backend won't start?**
- Check Python installation: `python --version`
- Install dependencies: `pip install -r requirements.txt`

**Frontend won't start?**
- Check Node.js: `node --version`
- Install dependencies: `npm install`

**Can't access the app?**
- Run health check: `health-check.bat`
- Check ports 3000 and 8000 are free

## 🎯 Usage Tips

1. **Be Specific** - Search for exact movie titles
2. **Set Preferences** - Configure genres, ratings, decades
3. **Try Different Movies** - Get varied recommendations
4. **Check Similar Movies** - Discover hidden gems
5. **Use Latest Movies** - Stay current with releases

## 📊 Tech Stack

**Backend:** FastAPI, Python, Scikit-learn, Pandas  
**Frontend:** Next.js, React, TypeScript, Tailwind CSS  
**ML:** TF-IDF Vectorization, Cosine Similarity  
**Database:** CSV-based movie database  
**Auth:** Firebase Authentication (optional)

---

**The Last Critic** - Your final word on what to watch! 🎬