import httpx
import asyncio
from typing import List, Optional
from app.models.search import SearchResult, ResultCategory
from app.core.config import settings


class YouTubeSearchService:
    """
    Searches YouTube for interviews, talks, panel appearances.
    Uses YouTube Data API v3.
    Free quota: 10,000 units/day.
    """

    BASE_URL = "https://www.googleapis.com/youtube/v3/search"

    async def search(self, name: str, description: Optional[str] = None) -> List[SearchResult]:
        if not settings.YOUTUBE_API_KEY:
            print("[YouTubeService] No API key, skipping.")
            return []

        # Build queries to target interview/talk content
        queries = [
            f"{name} interview",
            f"{name} podcast",
            f"{name} {description.split()[0] if description else ''} talk".replace("  ", " ").strip(),
        ]
        
        # Deduplicate queries to avoid redundant requests
        queries = list(dict.fromkeys(q for q in queries if q))

        all_results = []
        async with httpx.AsyncClient(timeout=15) as client:
            tasks = [
                client.get(
                    self.BASE_URL,
                    params={
                        "part": "snippet",
                        "q": query,
                        "type": "video",
                        "maxResults": 15,
                        "order": "relevance",
                        "key": settings.YOUTUBE_API_KEY
                    }
                )
                for query in queries
            ]
            
            try:
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                for resp in responses:
                    if isinstance(resp, Exception):
                        print(f"[YouTubeService] HTTP query error: {resp}")
                        continue
                    if resp.status_code != 200:
                        print(f"[YouTubeService] YouTube API error status: {resp.status_code}")
                        continue
                    
                    data = resp.json()
                    for item in data.get("items", []):
                        snippet = item.get("snippet", {})
                        video_id = item.get("id", {}).get("videoId", "")
                        if not video_id:
                            continue

                        all_results.append(SearchResult(
                            title=snippet.get("title", ""),
                            url=f"https://www.youtube.com/watch?v={video_id}",
                            source="YouTube",
                            category=ResultCategory.VIDEO,
                            summary=snippet.get("description", "")[:200],
                            thumbnail=snippet.get("thumbnails", {}).get("medium", {}).get("url"),
                            published_date=snippet.get("publishedAt", "")[:10],
                            relevance_score=0.8
                        ))

            except Exception as e:
                print(f"[YouTubeService] Error: {e}")

        # Deduplicate combined results by URL (keeping highest relevance score)
        deduped = {}
        for res in all_results:
            if not res.url:
                continue
            if res.url not in deduped or res.relevance_score > deduped[res.url].relevance_score:
                deduped[res.url] = res

        return list(deduped.values())
