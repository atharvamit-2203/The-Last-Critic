# Movie Recommendation Frontend

Modern Next.js frontend for the AI-powered movie recommendation system.

## Features

- 🎬 **Movie Search**: Instant search with autocomplete
- 🎯 **Personalized Preferences**: Set favorite genres, ratings, and decades
- 🤖 **AI Recommendations**: Get intelligent movie suggestions
- 📊 **Confidence Scores**: See how confident the AI is in its recommendations
- 🎨 **Modern UI**: Beautiful, responsive design with Tailwind CSS
- ⚡ **Real-time Updates**: Instant feedback as you change preferences

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **State Management**: React Hooks

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
# or
yarn install
```

2. Configure environment:
```bash
# .env.local is already created with default values
# Update if your backend is running on a different port
```

3. Run the development server:
```bash
npm run dev
# or
yarn dev
```

4. Open [http://localhost:3000](http://localhost:3000)

## Project Structure

```
frontend/
├── src/
│   ├── app/                  # Next.js app router
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Home page
│   │   └── globals.css      # Global styles
│   ├── components/          # React components
│   │   ├── Header.tsx
│   │   ├── MovieSearch.tsx
│   │   ├── PreferencesForm.tsx
│   │   ├── RecommendationResult.tsx
│   │   └── MovieCard.tsx
│   ├── services/           # API integration
│   │   └── api.ts
│   └── types/              # TypeScript types
│       └── index.ts
├── public/                 # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Features Overview

### Movie Search
- Search movies by title or genre
- Autocomplete suggestions
- Display movie details including rating, genres, and year

### User Preferences
- Select multiple favorite genres
- Set minimum rating threshold (0-10)
- Choose preferred decade (1970s-2020s)

### Recommendations
- AI-powered should-watch decision
- Confidence score for each recommendation
- Detailed analysis of why you should or shouldn't watch
- Similar movie suggestions based on content

## API Integration

The frontend communicates with the FastAPI backend at `http://localhost:8000`:

- `GET /api/movies` - Fetch available movies
- `POST /api/recommend` - Get personalized recommendations
- `GET /health` - Check API health

## Customization

### Styling
Modify `tailwind.config.js` to customize colors, fonts, and themes.

### API URL
Update `NEXT_PUBLIC_API_URL` in `.env.local` to point to your backend.

## Building for Production

```bash
npm run build
npm run start
```

## Deployment

Can be deployed to:
- Vercel (recommended for Next.js)
- Netlify
- AWS Amplify
- Docker containers

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
