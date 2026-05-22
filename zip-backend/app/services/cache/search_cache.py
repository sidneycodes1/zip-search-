from typing import Optional, Dict
import time
import hashlib
import json

class SearchCache:
    def __init__(self, ttl_seconds: int = 3600):
        self._store: Dict[str, dict] = {}
        self._ttl = ttl_seconds

    def _make_key(self, name: str, description: Optional[str]) -> str:
        raw = f"{name.lower().strip()}:{(description or '').lower().strip()}"
        return hashlib.md5(raw.encode()).hexdigest()

    def get(self, name: str, description: Optional[str]):
        key = self._make_key(name, description)
        entry = self._store.get(key)
        if not entry:
            return None
        if time.time() - entry["timestamp"] > self._ttl:
            del self._store[key]
            return None
        print(f"[Cache] HIT for '{name}'")
        return entry["results"]

    def set(self, name: str, description: Optional[str], results: list):
        key = self._make_key(name, description)
        self._store[key] = {
            "results": results,
            "timestamp": time.time()
        }
        print(f"[Cache] STORED {len(results)} results for '{name}'")

    def clear(self):
        self._store.clear()

cache = SearchCache(ttl_seconds=3600)
