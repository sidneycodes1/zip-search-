from typing import List, Optional
import httpx
import asyncio
from app.core.config import settings
from app.models.search import SearchResult, ResultCategory


class SerpAPISearchService:
    """
    Searches Google via SerpAPI to find general articles and links.
    """

    SEARCH_URL = "https://serpapi.com/search"

    async def search(self, name: str, description: Optional[str] = None) -> List[SearchResult]:
        print(f"[SerpAPIService] Key present: {bool(settings.SERPAPI_KEY)}")
        if not settings.SERPAPI_KEY:
            print("[SerpAPIService] No API key set, skipping.")
            return []

        q1 = f'"{name}"'
        if description:
            q1 += f' {description}'

        q2 = f'"{name}" interview OR podcast OR talk'

        queries = [q1, q2]
        
        # Deduplicate queries to avoid redundant requests
        queries = list(dict.fromkeys(q for q in queries if q))

        all_results: List[SearchResult] = []

        async with httpx.AsyncClient(timeout=15) as client:
            tasks = [
                client.get(
                    self.SEARCH_URL,
                    params={
                        "api_key": settings.SERPAPI_KEY,
                        "engine": "google",
                        "q": query,
                        "num": 15,
                    }
                )
                for query in queries
            ]
            
            try:
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                for resp in responses:
                    if isinstance(resp, Exception):
                        print(f"[SerpAPIService] Query HTTP error: {resp}")
                        continue
                    if resp.status_code != 200:
                        print(f"[SerpAPIService] SerpAPI error status: {resp.status_code}")
                        continue
                    
                    data = resp.json()
                    for result in data.get("organic_results", []):
                        title = result.get("title")
                        link = result.get("link")

                        if not title or not link:
                            continue

                        snippet = result.get("snippet", "")
                        summary = snippet[:200] if snippet else ""

                        all_results.append(
                            SearchResult(
                                title=title,
                                url=link,
                                source="Google Search",
                                category=ResultCategory.ARTICLE,
                                summary=summary,
                                thumbnail=result.get("thumbnail"),
                                relevance_score=0.85,
                            )
                        )

            except Exception as e:
                print(f"[SerpAPIService] Error: {e}")

        # Deduplicate combined results by URL (keeping highest relevance score)
        deduped = {}
        for res in all_results:
            if not res.url:
                continue
            if res.url not in deduped or res.relevance_score > deduped[res.url].relevance_score:
                deduped[res.url] = res

        return list(deduped.values())
