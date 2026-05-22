from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Zip"
    DEBUG: bool = False
    ALLOWED_ORIGINS: List[str] = [
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

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()