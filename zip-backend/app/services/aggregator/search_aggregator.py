import asyncio
from typing import Callable, List, Optional

from app.models.search import SearchResult
from app.services.osint.podcast_service import PodcastSearchService
from app.services.osint.news_service import NewsSearchService
from app.services.osint.youtube_service import YouTubeSearchService
from app.services.osint.social_service import SocialSearchService
from app.services.osint.spotify_service import SpotifySearchService
from app.services.osint.wikipedia_service import WikipediaSearchService
from app.services.osint.itunes_service import ItunesSearchService
from app.services.osint.serpapi_service import SerpAPISearchService
from app.services.cache.search_cache import cache
from app.services.scoring.confidence_scorer import scorer

class SearchAggregator:
    """
    Runs all OSINT services in parallel and merges/deduplicates results.
    """

    def __init__(self):
        self.podcast_service = PodcastSearchService()
        self.news_service = NewsSearchService()
        self.youtube_service = YouTubeSearchService()
        self.social_service = SocialSearchService()
        self.spotify_service = SpotifySearchService()
        self.wikipedia_service = WikipediaSearchService()
        self.itunes_service = ItunesSearchService()
        self.serpapi_service = SerpAPISearchService()
        self.sources_searched: List[str] = []

    async def search(
        self,
        name: str,
        description: Optional[str] = None,
        on_progress: Optional[Callable[[int], None]] = None,
    ) -> List[SearchResult]:

        cached = cache.get(name, description)
        if cached:
            return cached

        service_tasks = [
            ("Listen Notes", self.podcast_service.search(name, description)),
            ("News", self.news_service.search(name, description)),
            ("YouTube", self.youtube_service.search(name, description)),
            ("Social", self.social_service.search(name, description)),
            ("Spotify", self.spotify_service.search(name, description)),
            ("Wikipedia", self.wikipedia_service.search(name, description)),
            ("iTunes", self.itunes_service.search(name, description)),
            ("Google Search", self.serpapi_service.search(name, description)),
        ]

        service_names = [service_name for service_name, _ in service_tasks]
        self.sources_searched = service_names
        print(f"[Aggregator] Searching sources: {', '.join(service_names)}")

        if on_progress:
            on_progress(15)

        results_sets = await asyncio.gather(
            *(task for _, task in service_tasks),
            return_exceptions=True,
        )

        if on_progress:
            on_progress(70)

        all_results: List[SearchResult] = []

        for service_name, result_set in zip(service_names, results_sets):
            if isinstance(result_set, Exception):
                print(f"[Aggregator] {service_name} failed: {result_set}")
                continue
            if result_set:
                all_results.extend(result_set)

        if on_progress:
            on_progress(75)

        seen_urls = set()
        deduped: List[SearchResult] = []
        for result in all_results:
            if result.url and result.url not in seen_urls:
                seen_urls.add(result.url)
                deduped.append(result)

        deduped.sort(key=lambda r: r.relevance_score, reverse=True)
        deduped = scorer.score(deduped)
        cache.set(name, description, deduped)
        return deduped
