@echo off
echo 📦 Setting up Git and pushing to GitHub...
echo ==========================================

echo Step 1: Initialize Git repository...
git init

echo Step 2: Add all files...
git add .

echo Step 3: Commit changes...
git commit -m "The Last Critic - Movie Recommendation System"

echo Step 4: Create GitHub repository...
echo Please create a new repository on GitHub: https://github.com/new
echo Repository name: the-last-critic
pause

set /p repo_url="Enter your GitHub repository URL (https://github.com/username/the-last-critic.git): "

echo Step 5: Add remote origin...
git remote add origin %repo_url%

echo Step 6: Push to GitHub...
git branch -M main
git push -u origin main

echo ✅ Code pushed to GitHub!
echo 🚀 Now deploying to Vercel...

echo Step 7: Install Vercel CLI...
npm install -g vercel

echo Step 8: Deploy to Vercel...
vercel --prod

echo ✅ Deployment Complete!
pause