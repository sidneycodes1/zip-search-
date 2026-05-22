import re
import urllib.parse
from typing import List, Optional
import httpx
from app.models.search import SearchResult, ResultCategory


class WikipediaSearchService:
    """
    Searches Wikipedia for matching pages using the Wikipedia REST & query APIs.
    """

    async def search(self, name: str, description: Optional[str] = None) -> List[SearchResult]:
        results: List[SearchResult] = []
        main_page_title: Optional[str] = None
        main_page_url: Optional[str] = None

        # 1. First try the summary endpoint
        encoded_name = urllib.parse.quote(name)
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_name}"

        headers = {"User-Agent": "Zip/0.1.0 (contact@zip.com) python-httpx/0.24.1"}
        async with httpx.AsyncClient(timeout=10, headers=headers) as client:
            # 2. Get main page summary
            try:
                resp = await client.get(summary_url)
                if resp.status_code == 200:
                    page = resp.json()
                    extract = page.get("extract")
                    if extract:
                        main_page_title = page.get("title")
                        content_urls = page.get("content_urls", {})
                        main_page_url = content_urls.get("desktop", {}).get("page")
                        
                        thumbnail_dict = page.get("thumbnail")
                        thumbnail = thumbnail_dict.get("source") if thumbnail_dict else None

                        results.append(
                            SearchResult(
                                title=f"{main_page_title} — Wikipedia",
                                url=main_page_url or f"https://en.wikipedia.org/wiki/{urllib.parse.quote(main_page_title.replace(' ', '_'))}",
                                source="Wikipedia",
                                category=ResultCategory.ARTICLE,
                                summary=extract[:300],
                                thumbnail=thumbnail,
                                relevance_score=0.95,
                            )
                        )
                elif resp.status_code != 404:
                    print(f"[WikipediaService] Summary HTTP error: {resp.status_code}")
            except Exception as e:
                print(f"[WikipediaService] Summary endpoint error: {e}")

            # 3. Also search for related pages
            try:
                search_url = "https://en.wikipedia.org/w/api.php"
                resp = await client.get(
                    search_url,
                    params={
                        "action": "query",
                        "list": "search",
                        "srsearch": name,
                        "format": "json",
                        "srlimit": 8,
                    }
                )
                resp.raise_for_status()
                data = resp.json()

                for item in data.get("query", {}).get("search", []):
                    title = item.get("title")
                    if not title:
                        continue

                    # 4. Check if it's NOT the main page (if we found a main page)
                    if main_page_title and title.lower() == main_page_title.lower():
                        continue

                    snippet = item.get("snippet", "")
                    clean_snippet = re.sub(r"<[^>]*>", "", snippet)

                    wiki_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"

                    results.append(
                        SearchResult(
                            title=f"{title} — Wikipedia",
                            url=wiki_url,
                            source="Wikipedia",
                            category=ResultCategory.ARTICLE,
                            summary=clean_snippet[:300],
                            relevance_score=0.80,
                        )
                    )
            except Exception as e:
                print(f"[WikipediaService] Search endpoint error: {e}")

        return results
