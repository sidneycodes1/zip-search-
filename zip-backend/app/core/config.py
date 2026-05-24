from pydantic_settings import BaseSettings
from typing import List, Union
import json

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Zip"
    DEBUG: bool = False
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003"
    ]

    # API Keys
    NEWSAPI_KEY: str = ""
    YOUTUBE_API_KEY: str = ""
    LISTENNOTES_API_KEY: str = ""
    SPOTIFY_CLIENT_ID: str = ""
    SPOTIFY_CLIENT_SECRET: str = ""
    SERPAPI_KEY: str = ""
    FACEBOOK_APP_ID: str = ""
    FACEBOOK_APP_SECRET: str = ""

    # Redis (job queue)
    REDIS_URL: str = "redis://localhost:6379"

    # IPFS (for onchain phase)
    PINATA_API_KEY: str = ""
    PINATA_SECRET_KEY: str = ""

    # Search limits
    MAX_SEARCH_RESULTS: int = 50
    SEARCH_TIMEOUT_SECONDS: int = 30

    def get_allowed_origins(self) -> List[str]:
        if isinstance(self.ALLOWED_ORIGINS, str):
            if self.ALLOWED_ORIGINS.startswith("["):
                return json.loads(self.ALLOWED_ORIGINS)
            return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]
        return self.ALLOWED_ORIGINS

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()