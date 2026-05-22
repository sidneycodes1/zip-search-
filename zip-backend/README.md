# Zip — Backend API

Public figure intelligence search engine. Input a name, description, and optional photo — get back podcasts, news articles, interviews, videos, and social profiles from across the internet.

---

## Architecture

```
POST /api/v1/search          ← Submit search job
GET  /api/v1/search/status/{job_id}  ← Poll for results
GET  /api/v1/health          ← Health check
```

**Search pipeline (runs in parallel):**
- 🎙️ Listen Notes → podcast appearances
- 📰 NewsAPI + Google News → articles and press
- 🎥 YouTube API → interviews and talks
- 👤 Maigret → social profiles across 3000+ sites
- 🧠 DeepFace → photo verification (if photo uploaded)

---

## Setup

### 1. Clone and install

```bash
cd zip-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API keys

```bash
cp .env.example .env
# Fill in your API keys in .env
```

**Get your free API keys:**
| Service | Free Tier | Link |
|---|---|---|
| NewsAPI | 100 req/day | https://newsapi.org |
| YouTube Data API | 10,000 units/day | https://console.cloud.google.com |
| Listen Notes | 10 req/day | https://www.listennotes.com/api |

### 3. Run

```bash
uvicorn app.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

---

## Example Request

```bash
curl -X POST http://localhost:8000/api/v1/search \
  -F "name=Elon Musk" \
  -F "description=CEO Tesla SpaceX"
```

Response:
```json
{
  "job_id": "abc-123",
  "status": "pending",
  "progress": 0
}
```

Then poll:
```bash
curl http://localhost:8000/api/v1/search/status/abc-123
```

---

## With Photo Upload

```bash
curl -X POST http://localhost:8000/api/v1/search \
  -F "name=John Doe" \
  -F "description=VP Marketing Opay" \
  -F "photo=@/path/to/photo.jpg"
```

The photo triggers DeepFace verification — results with thumbnails get cross-checked against the uploaded face, filtering out wrong people with the same name.

---

## Project Structure

```
zip-backend/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── core/
│   │   └── config.py              # Environment config
│   ├── api/routes/
│   │   ├── search.py              # Search endpoints
│   │   └── health.py              # Health check
│   ├── models/
│   │   └── search.py              # Pydantic data models
│   └── services/
│       ├── osint/
│       │   ├── podcast_service.py # Listen Notes
│       │   ├── news_service.py    # NewsAPI + Google News
│       │   ├── youtube_service.py # YouTube API
│       │   └── social_service.py  # Maigret wrapper
│       ├── face/
│       │   └── face_matcher.py    # DeepFace photo verification
│       └── aggregator/
│           └── search_aggregator.py # Parallel execution + merge
├── requirements.txt
├── .env.example
└── README.md
```

---

## Phase 2 — Onchain (coming later)

- Search receipts on Base (proof of research)
- IPFS report storage via Pinata
- NFT access control
- ZK privacy proofs
