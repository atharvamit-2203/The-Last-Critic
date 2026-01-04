@echo off
echo 🚀 Deploying The Last Critic to Vercel...
echo ==========================================

echo 📦 Step 1: Installing Vercel CLI...
npm install -g vercel

echo 📁 Step 2: Initializing project...
if not exist ".git" (
    git init
    git add .
    git commit -m "Deploy The Last Critic to Vercel"
)

echo 🌐 Step 3: Deploying to Vercel...
vercel --prod

echo ✅ Deployment Complete!
echo 🎬 Your movie app is now live!
echo 📱 Check your Vercel dashboard for the URL

pause