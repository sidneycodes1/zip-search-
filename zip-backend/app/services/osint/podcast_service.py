import httpx
from typing import List, Optional
from app.models.search import SearchResult, ResultCategory
from app.core.config import settings


class PodcastSearchService:
    """
    Searches Listen Notes API for podcast appearances.
    Listen Notes indexes 3M+ podcasts — best source for finding
    when a person was a guest on a show.
    Docs: https://www.listennotes.com/api/docs/
    """

    BASE_URL = "https://listen-api.listennotes.com/api/v2"

    async def search(self, name: str, description: Optional[str] = None) -> List[SearchResult]:
        if not settings.LISTENNOTES_API_KEY:
            print("[PodcastService] No API key set, skipping.")
            return []

        query = name
        if description:
            # Adding context improves relevance e.g. "John Doe Opay marketing"
            keywords = self._extract_keywords(description)
            query = f"{name} {keywords}"

        results = []
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/search",
                    params={
                        "q": query,
                        "type": "episode",
                        "language": "English",
                        "sort_by_date": 1,
                        "only_in": "title,description",
                    },
                    headers={"X-ListenAPI-Key": settings.LISTENNOTES_API_KEY}
                )
                resp.raise_for_status()
                data = resp.json()

                for ep in data.get("results", [])[:10]:
                    results.append(SearchResult(
                        title=ep.get("title_original", "Untitled Episode"),
                        url=ep.get("listennotes_url", ""),
                        source="Listen Notes",
                        category=ResultCategory.PODCAST,
                        summary=self._truncate(ep.get("description_original", ""), 200),
                        thumbnail=ep.get("image", None),
                        published_date=self._format_date(ep.get("pub_date_ms")),
                        relevance_score=0.9
                    ))

            except httpx.HTTPError as e:
                print(f"[PodcastService] HTTP error: {e}")

        return results

    def _extract_keywords(self, description: str) -> str:
        """Pull company/role keywords from description for better search."""
        stop_words = {"a", "an", "the", "is", "at", "for", "and", "or", "of", "in"}
        words = [w for w in description.split() if w.lower() not in stop_words]
        return " ".join(words[:4])

    def _truncate(self, text: str, max_len: int) -> str:
        return text[:max_len] + "..." if len(text) > max_len else text

    def _format_date(self, ms: Optional[int]) -> Optional[str]:
        if not ms:
            return None
        from datetime import datetime
        return datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d")
