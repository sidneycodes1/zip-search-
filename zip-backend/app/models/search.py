from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Any
from enum import Enum

class ResultCategory(str, Enum):
    PODCAST = "podcast"
    NEWS = "news"
    VIDEO = "video"
    SOCIAL = "social"
    ARTICLE = "article"
    OTHER = "other"

class SearchRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Full name of the person")
    description: Optional[str] = Field(None, max_length=300, description="Brief context e.g. 'VP Marketing at Opay'")
    # photo is handled as multipart upload separately
    photo: Optional[Any] = None

    @model_validator(mode='before')
    @classmethod
    def check_name_or_photo(cls, data: Any) -> Any:
        if isinstance(data, dict):
            name = data.get('name')
            photo = data.get('photo')
            if not name and not photo:
                raise ValueError('At least one of name or photo must be provided')
        return data

class SearchResult(BaseModel):
    title: str
    url: str
    source: str
    category: ResultCategory
    summary: Optional[str] = None
    thumbnail: Optional[str] = None
    published_date: Optional[str] = None
    relevance_score: float = Field(default=1.0, ge=0.0, le=1.0)
    face_matched: Optional[bool] = None  # True if photo was verified
    confidence_label: str = "medium"

class SearchResponse(BaseModel):
    query_name: str
    query_description: Optional[str]
    total_results: int
    results: List[SearchResult]
    sources_searched: List[str]
    search_duration_seconds: float
    job_id: str  # For async polling

class JobStatus(BaseModel):
    job_id: str
    status: str  # pending | running | complete | failed
    progress: int  # 0-100
    results: Optional[SearchResponse] = None
    error: Optional[str] = None
