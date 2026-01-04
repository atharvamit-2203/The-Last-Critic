#!/bin/bash

echo "🚀 The Last Critic - Deployment Script"
echo "======================================"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit - The Last Critic Movie Recommendation System"
fi

echo ""
echo "Choose deployment platform:"
echo "1. Vercel (Recommended - Full Stack)"
echo "2. Netlify (Frontend) + Railway (Backend)"
echo "3. Railway (Full Stack)"
echo "4. Manual Docker Setup"

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "🔥 Deploying to Vercel..."
        echo "1. Install Vercel CLI: npm i -g vercel"
        echo "2. Run: vercel"
        echo "3. Follow the prompts"
        echo "4. Your app will be live at: https://your-app.vercel.app"
        ;;
    2)
        echo "🌐 Deploying Frontend to Netlify + Backend to Railway..."
        echo "Frontend (Netlify):"
        echo "1. Push code to GitHub"
        echo "2. Connect GitHub to Netlify"
        echo "3. Set build directory: frontend"
        echo ""
        echo "Backend (Railway):"
        echo "1. Connect GitHub to Railway"
        echo "2. Deploy backend folder"
        echo "3. Update NEXT_PUBLIC_API_URL in frontend"
        ;;
    3)
        echo "🚂 Deploying to Railway..."
        echo "1. Push code to GitHub"
        echo "2. Connect GitHub to Railway"
        echo "3. Railway will auto-deploy using railway.yml"
        ;;
    4)
        echo "🐳 Manual Docker Setup..."
        echo "Backend:"
        echo "docker build -f Dockerfile.backend -t movie-backend ."
        echo "docker run -p 8000:8000 movie-backend"
        echo ""
        echo "Frontend:"
        echo "docker build -f Dockerfile.frontend -t movie-frontend ."
        echo "docker run -p 3000:3000 movie-frontend"
        ;;
esac

echo ""
echo "✅ Deployment files created!"
echo "📁 Files added:"
echo "   - vercel.json (Vercel config)"
echo "   - netlify.toml (Netlify config)"
echo "   - Dockerfile.backend (Backend container)"
echo "   - Dockerfile.frontend (Frontend container)"
echo "   - railway.yml (Railway config)"
echo ""
echo "🔗 Quick Deploy Links:"
echo "   Vercel: https://vercel.com/new"
echo "   Netlify: https://app.netlify.com/start"
echo "   Railway: https://railway.app/new"