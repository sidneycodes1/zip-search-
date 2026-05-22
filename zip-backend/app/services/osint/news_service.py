import httpx
import asyncio
from typing import List, Optional
from app.models.search import SearchResult, ResultCategory
from app.core.config import settings


class NewsSearchService:
    """
    Pulls news articles and press mentions about a person.
    Uses NewsAPI (paid) + pygooglenews fallback (free).
    """

    NEWSAPI_URL = "https://newsapi.org/v2/everything"

    async def search(self, name: str, description: Optional[str] = None) -> List[SearchResult]:
        results = []

        # Try NewsAPI first (higher quality, structured)
        if settings.NEWSAPI_KEY:
            results += await self._search_newsapi(name, description)

        # Always try Google News scrape as supplement
        results += await self._search_google_news(name, description)

        # Deduplicate all combined results by URL (keeping highest relevance score)
        deduped = {}
        for res in results:
            if not res.url:
                continue
            if res.url not in deduped or res.relevance_score > deduped[res.url].relevance_score:
                deduped[res.url] = res

        return list(deduped.values())

    async def _search_newsapi(self, name: str, description: Optional[str]) -> List[SearchResult]:
        queries = [
            f'"{name}"',
            f'"{name}" interview',
            f'"{name}" {description.split()[0] if description else ""}'.strip(),
        ]
        
        # Deduplicate queries to avoid redundant requests
        queries = list(dict.fromkeys(q for q in queries if q))

        all_results = []
        async with httpx.AsyncClient(timeout=15) as client:
            tasks = [
                client.get(
                    self.NEWSAPI_URL,
                    params={
                        "q": query,
                        "sortBy": "relevancy",
                        "language": "en",
                        "pageSize": 10,
                        "apiKey": settings.NEWSAPI_KEY
                    }
                )
                for query in queries
            ]
            
            try:
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                for resp in responses:
                    if isinstance(resp, Exception):
                        print(f"[NewsService] NewsAPI query HTTP error: {resp}")
                        continue
                    if resp.status_code != 200:
                        print(f"[NewsService] NewsAPI error status: {resp.status_code}")
                        continue
                    
                    data = resp.json()
                    for article in data.get("articles", []):
                        all_results.append(SearchResult(
                            title=article.get("title", ""),
                            url=article.get("url", ""),
                            source=article.get("source", {}).get("name", "NewsAPI"),
                            category=ResultCategory.NEWS,
                            summary=article.get("description", ""),
                            thumbnail=article.get("urlToImage"),
                            published_date=article.get("publishedAt", "")[:10],
                            relevance_score=0.85
                        ))

            except Exception as e:
                print(f"[NewsService] NewsAPI error: {e}")

        # Deduplicate internal query results by URL (keeping highest relevance score)
        deduped = {}
        for res in all_results:
            if not res.url:
                continue
            if res.url not in deduped or res.relevance_score > deduped[res.url].relevance_score:
                deduped[res.url] = res

        return list(deduped.values())

    async def _search_google_news(self, name: str, description: Optional[str]) -> List[SearchResult]:
        """
        Lightweight Google News RSS scrape — no API key needed.
        Returns recent news snippets.
        """
        results = []
        base = name.replace(" ", "+")
        if description:
            words = description.split()[:3]
            extra = "+".join(words)
            query = f"{base}+({extra})"
        else:
            query = base

        rss_url = f"https://news.google.com/rss/search?q={query}&hl=en&gl=US&ceid=US:en"

        async with httpx.AsyncClient(timeout=10) as client:
            try:
                resp = await client.get(rss_url, follow_redirects=True)
                resp.raise_for_status()

                # Basic RSS parse without external lib
                import xml.etree.ElementTree as ET
                root = ET.fromstring(resp.text)
                items = root.findall(".//item")[:15]

                for item in items:
                    title = item.findtext("title", "")
                    link = item.findtext("link", "")
                    pub_date = item.findtext("pubDate", "")
                    source_tag = item.find("source")
                    source_name = source_tag.text if source_tag is not None else "Google News"

                    if not link:
                        continue

                    results.append(SearchResult(
                        title=title,
                        url=link,
                        source=source_name,
                        category=ResultCategory.NEWS,
                        published_date=pub_date[:16] if pub_date else None,
                        relevance_score=0.75
                    ))

            except Exception as e:
                print(f"[NewsService] Google News RSS error: {e}")

        return results
