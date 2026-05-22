import base64
import asyncio
from typing import List, Optional
import httpx
from app.core.config import settings
from app.models.search import SearchResult, ResultCategory


class SpotifySearchService:
    """
    Searches Spotify podcast episodes using the Spotify Web API.
    """

    TOKEN_URL = "https://accounts.spotify.com/api/token"
    SEARCH_URL = "https://api.spotify.com/v1/search"

    async def search(self, name: str, description: Optional[str] = None) -> List[SearchResult]:
        if not settings.SPOTIFY_CLIENT_ID or not settings.SPOTIFY_CLIENT_SECRET:
            print("[SpotifyService] No credentials set, skipping.")
            return []

        try:
            access_token = await self._get_access_token()
            if not access_token:
                return []

            return await self._search_episodes(name, access_token)
        except Exception as e:
            print(f"[SpotifyService] Error: {e}")
            return []

    async def _get_access_token(self) -> Optional[str]:
        credentials = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

        async with httpx.AsyncClient(timeout=15) as client:
            try:
                resp = await client.post(
                    self.TOKEN_URL,
                    data={"grant_type": "client_credentials"},
                    headers={
                        "Authorization": f"Basic {encoded_credentials}",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                )
                resp.raise_for_status()
                return resp.json().get("access_token")
            except Exception as e:
                print(f"[SpotifyService] Token error: {e}")
                return None

    async def _search_episodes(self, name: str, access_token: str) -> List[SearchResult]:
        queries = [f"{name}", f"{name} interview", f"{name} podcast"]
        
        # Deduplicate queries to avoid redundant requests
        queries = list(dict.fromkeys(q for q in queries if q))

        all_results: List[SearchResult] = []

        async with httpx.AsyncClient(timeout=15) as client:
            tasks = [
                client.get(
                    self.SEARCH_URL,
                    params={
                        "q": query,
                        "type": "episode",
                        "limit": 15,
                        "market": "US",
                    },
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                for query in queries
            ]
            
            try:
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                for resp in responses:
                    if isinstance(resp, Exception):
                        print(f"[SpotifyService] Query HTTP error: {resp}")
                        continue
                    if resp.status_code != 200:
                        print(f"[SpotifyService] Spotify API error status: {resp.status_code}")
                        continue
                    
                    data = resp.json()
                    for episode in data.get("episodes", {}).get("items", []):
                        if not episode:
                            continue

                        spotify_url = episode.get("external_urls", {}).get("spotify", "")
                        if not spotify_url:
                            continue

                        images = episode.get("images", [])
                        thumbnail = images[0].get("url") if images else None

                        all_results.append(
                            SearchResult(
                                title=episode.get("name", "Untitled Episode"),
                                url=spotify_url,
                                source="Spotify",
                                category=ResultCategory.PODCAST,
                                summary=(episode.get("description") or "")[:200],
                                thumbnail=thumbnail,
                                published_date=episode.get("release_date"),
                                relevance_score=0.88,
                            )
                        )

            except Exception as e:
                print(f"[SpotifyService] Search error: {e}")

        # Deduplicate combined results by URL (keeping highest relevance score)
        deduped = {}
        for res in all_results:
            if not res.url:
                continue
            if res.url not in deduped or res.relevance_score > deduped[res.url].relevance_score:
                deduped[res.url] = res

        return list(deduped.values())
