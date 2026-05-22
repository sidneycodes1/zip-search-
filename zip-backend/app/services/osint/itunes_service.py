from typing import List, Optional
import httpx
from app.models.search import SearchResult, ResultCategory


class ItunesSearchService:
    """
    Searches Apple Podcasts using the iTunes Search API.
    """

    SEARCH_URL = "https://itunes.apple.com/search"

    async def search(self, name: str, description: Optional[str] = None) -> List[SearchResult]:
        queries = [name, f"{name} interview", f"{name} podcast"]
        if description:
            first_word = description.split()[0]
            queries.append(f"{name} {first_word}")
        
        all_results = []
        seen_urls = set()
        
        async with httpx.AsyncClient(timeout=15) as client:
            for query in queries:
                try:
                    resp = await client.get(
                        "https://itunes.apple.com/search",
                        params={
                            "term": query,
                            "media": "podcast",
                            "entity": "podcastEpisode",
                            "limit": 10
                        }
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    
                    for result in data.get("results", []):
                        url = result.get("trackViewUrl", "")
                        if not url or url in seen_urls:
                            continue
                        seen_urls.add(url)
                        
                        title = result.get("trackName", "")
                        if not title:
                            continue
                        
                        all_results.append(SearchResult(
                            title=title,
                            url=url,
                            source="Apple Podcasts",
                            category=ResultCategory.PODCAST,
                            summary=result.get("description", "")[:200],
                            thumbnail=result.get("artworkUrl100"),
                            published_date=result.get("releaseDate", "")[:10],
                            relevance_score=0.85
                        ))
                except Exception as e:
                    print(f"[iTunesService] Error for query '{query}': {e}")
        
        return all_results
