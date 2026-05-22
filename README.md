# Zip — Public Figure Intelligence Search Engine

Find anyone's public digital footprint — podcasts, news, 
videos, social profiles — in seconds.

## What It Does

Search by name, description, or photo. Zip searches across:
- YouTube interviews and talks
- Spotify and Apple Podcasts appearances  
- News articles from 20+ sources
- Google Search results
- Wikipedia profiles
- Social media profiles

Upload a photo for face-verified results — Zip cross-checks 
every result against the uploaded face.

## Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: Python FastAPI, DeepFace, InsightFace
- **Search**: YouTube API, SerpAPI, Spotify API, NewsAPI, 
  Listen Notes, iTunes, Wikipedia
- **Web3**: RainbowKit, wagmi, Base (Phase 2)

## Setup

### Backend
```bash
cd zip-backend
py -3.11 -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Fill in your API keys in .env
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd zip-frontend
npm install
cp .env.example .env.local
# Fill in your values in .env.local
npm run dev
```

## API Keys Needed

| Key | Free Tier | Link |
|-----|-----------|------|
| YouTube Data API | 10,000 units/day | console.cloud.google.com |
| NewsAPI | 100 req/day | newsapi.org |
| SerpAPI | 100 searches/month | serpapi.com |
| Spotify | Free | developer.spotify.com |
| Listen Notes | 10 req/day | listennotes.com/api |

## Project Status

- Phase 1: Search engine + UI ✅
- Phase 2: Onchain receipts (planned)
- Phase 3: ZK privacy (planned)
