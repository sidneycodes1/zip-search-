from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from typing import Optional
import uuid
import time

from app.models.search import SearchResponse, JobStatus
from app.services.aggregator.search_aggregator import SearchAggregator
from app.services.face.face_matcher import FaceMatcher
from app.core.config import settings

router = APIRouter()

# In-memory job store (replace with Redis in production)
job_store: dict = {}

aggregator = SearchAggregator()
face_matcher = FaceMatcher()


async def run_search_job(
    job_id: str,
    name: Optional[str],
    description: Optional[str],
    photo_bytes: Optional[bytes]
):
    """Background task that runs the full search pipeline."""
    try:
        job_store[job_id]["status"] = "running"
        job_store[job_id]["progress"] = 10
        start_time = time.time()

        # Step 1 — Run all OSINT sources in parallel
        # If no name is provided but we have a photo, we pass an empty string to aggregator
        # so it can search broadly (some sources might return default/trending feeds)
        raw_results = await aggregator.search(
            name=name or "",
            description=description,
            on_progress=lambda p: job_store[job_id].update({"progress": p})
        )

        job_store[job_id]["progress"] = 80

        # Step 2 — If photo provided, run face matching to filter results
        if photo_bytes:
            raw_results = await face_matcher.filter_by_face(
                results=raw_results,
                photo_bytes=photo_bytes
            )

        job_store[job_id]["progress"] = 95

        duration = time.time() - start_time

        response = SearchResponse(
            query_name=name,
            query_description=description,
            total_results=len(raw_results),
            results=raw_results,
            sources_searched=aggregator.sources_searched,
            search_duration_seconds=round(duration, 2),
            job_id=job_id
        )

        job_store[job_id]["status"] = "complete"
        job_store[job_id]["progress"] = 100
        job_store[job_id]["results"] = response

    except Exception as e:
        job_store[job_id]["status"] = "failed"
        job_store[job_id]["error"] = str(e)


@router.post("/search", response_model=JobStatus)
async def start_search(
    background_tasks: BackgroundTasks,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
):
    """
    Start a search job. Returns a job_id immediately.
    Poll /search/status/{job_id} for results.
    """
    if not name and not photo:
        raise HTTPException(status_code=400, detail="At least one of name or photo must be provided")

    if name is not None and len(name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Name too short")

    job_id = str(uuid.uuid4())
    photo_bytes = await photo.read() if photo else None

    job_store[job_id] = {
        "status": "pending",
        "progress": 0,
        "results": None,
        "error": None
    }

    background_tasks.add_task(
        run_search_job,
        job_id=job_id,
        name=name.strip() if name else None,
        description=description,
        photo_bytes=photo_bytes
    )

    return JobStatus(job_id=job_id, status="pending", progress=0)


@router.get("/search/status/{job_id}", response_model=JobStatus)
async def get_search_status(job_id: str):
    """Poll this endpoint to get search progress and results."""
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatus(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"],
        results=job.get("results"),
        error=job.get("error")
    )
