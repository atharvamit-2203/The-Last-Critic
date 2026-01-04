@echo off
echo 🚀 Deploying Frontend Only to Vercel...
echo ========================================

echo Step 1: Navigate to frontend directory...
cd frontend

echo Step 2: Install Vercel CLI...
npm install -g vercel

echo Step 3: Deploy frontend...
vercel --prod

echo ✅ Frontend deployed!
echo ⚠️  Note: Backend APIs won't work until backend is deployed separately

pause