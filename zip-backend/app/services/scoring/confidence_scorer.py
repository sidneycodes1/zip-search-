from app.models.search import SearchResult

class ConfidenceScorer:
    
    HIGH_SOURCES = ["Wikipedia", "Spotify", "Apple Podcasts", "YouTube"]
    MEDIUM_SOURCES = ["Google Search", "Listen Notes", "News"]
    LOW_SOURCES = ["Reddit", "Social"]

    def score(self, results: list) -> list:
        for result in results:
            result.confidence_label = self._get_label(result)
        return results

    def _get_label(self, result: SearchResult) -> str:
        # Face verified = always high confidence
        if result.face_matched is True:
            return "high"
        
        # Score based on source + relevance
        if result.source in self.HIGH_SOURCES and result.relevance_score >= 0.8:
            return "high"
        elif result.relevance_score >= 0.6:
            return "medium"
        else:
            return "low"

scorer = ConfidenceScorer()
