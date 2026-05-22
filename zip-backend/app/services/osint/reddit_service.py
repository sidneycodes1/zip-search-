from datetime import datetime, timezone
from typing import List, Optional

import httpx

from app.models.search import ResultCategory, SearchResult


class RedditSearchService:
    """
    Searches Reddit's public JSON API for relevant public posts.
    """

    SEARCH_URL = "https://www.reddit.com/search.json"

    async def search(self, name: str, description: Optional[str] = None) -> List[SearchResult]:
        results: List[SearchResult] = []
        headers = {"User-Agent": "Zip Research Tool 1.0"}

        async with httpx.AsyncClient(timeout=15, headers=headers) as client:
            try:
                resp = await client.get(
                    self.SEARCH_URL,
                    params={
                        "q": name,
                        "sort": "relevance",
                        "limit": 10,
                        "type": "link",
                    },
                )
                if resp.status_code == 429:
                    print("[RedditService] Rate limited by Reddit, skipping.")
                    return []
                resp.raise_for_status()
                data = resp.json()

                for child in data.get("data", {}).get("children", []):
                    post = child.get("data", {})
                    title = post.get("title", "")
                    if not title or name.lower() not in title.lower():
                        continue

                    is_self = bool(post.get("is_self"))
                    selftext = post.get("selftext", "") if is_self else ""

                    results.append(
                        SearchResult(
                            title=title,
                            url=f"https://reddit.com{post.get('permalink', '')}",
                            source=f"Reddit r/{post.get('subreddit', 'reddit')}",
                            category=ResultCategory.ARTICLE,
                            summary=self._truncate(selftext, 200) if selftext else "",
                            published_date=self._format_timestamp(post.get("created_utc")),
                            relevance_score=0.70,
                        )
                    )

            except httpx.HTTPStatusError as e:
                if e.response is not None and e.response.status_code == 429:
                    print("[RedditService] Rate limited by Reddit, skipping.")
                    return []
                print(f"[RedditService] HTTP status error: {e}")
            except httpx.HTTPError as e:
                print(f"[RedditService] HTTP error: {e}")
            except Exception as e:
                print(f"[RedditService] Unexpected error: {e}")

        return results

    def _truncate(self, text: str, max_len: int) -> str:
        return text[:max_len] + "..." if text and len(text) > max_len else text

    def _format_timestamp(self, timestamp: Optional[float]) -> Optional[str]:
        if not timestamp:
            return None
        return datetime.fromtimestamp(float(timestamp), tz=timezone.utc).strftime("%Y-%m-%d")
