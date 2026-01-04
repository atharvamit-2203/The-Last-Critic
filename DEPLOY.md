# 🚀 Deploy The Last Critic to Vercel

## Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "The Last Critic - Movie Recommendation System"
```

Create repository on GitHub: https://github.com/new
Repository name: `the-last-critic`

```bash
git remote add origin https://github.com/YOUR_USERNAME/the-last-critic.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy to Vercel
1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Select "the-last-critic"
4. Click "Deploy"

**OR use CLI:**
```bash
npm install -g vercel
vercel --prod
```

## ✅ Your app will be live at:
`https://the-last-critic-[random].vercel.app`