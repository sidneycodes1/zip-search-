from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Request
from typing import Optional
import uuid
import time
import re

from app.models.search import SearchResponse, JobStatus
from app.services.aggregator.search_aggregator import SearchAggregator
from app.services.face.face_matcher import FaceMatcher
from app.core.config import settings

router = APIRouter()

# In-memory job store (replace with Redis in production)
job_store: dict = {}

# Simple in-memory rate limiting store: IP -> list of timestamps
rate_limit_store: dict = {}

aggregator = SearchAggregator()
face_matcher = FaceMatcher()


def check_rate_limit(client_ip: str, limit: int, window: int) -> bool:
    current_time = time.time()
    timestamps = rate_limit_store.get(client_ip, [])
    # Filter out timestamps older than the window
    timestamps = [t for t in timestamps if current_time - t < window]
    if len(timestamps) >= limit:
        return False
    timestamps.append(current_time)
    rate_limit_store[client_ip] = timestamps
    return True


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
        # Sanitize exception message to avoid exposing internal paths/details to the client
        print(f"[SearchJobError] Detailed error: {e}")
        job_store[job_id]["error"] = "An internal error occurred while processing the search."


@router.post("/search", response_model=JobStatus)
async def start_search(
    request: Request,
    background_tasks: BackgroundTasks,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
):
    """
    Start a search job. Returns a job_id immediately.
    Poll /search/status/{job_id} for results.
    """
    # 1. Rate Limiting Pass
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip, limit=5, window=60):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Maximum 5 searches per minute.")

    # 2. Basic Input Validation
    if not name and not photo:
        raise HTTPException(status_code=400, detail="At least one of name or photo must be provided")

    # Name validation & sanitization
    if name is not None:
        name_str = name.strip()
        if len(name_str) < 2 or len(name_str) > 100:
            raise HTTPException(status_code=400, detail="Name must be between 2 and 100 characters")
        # Allow alphanumeric, spaces, hyphens, dots, apostrophes, and standard accented chars
        if not re.match(r"^[a-zA-Z0-9\s'\.\-\u00C0-\u00FF]+$", name_str):
            raise HTTPException(status_code=400, detail="Name contains invalid characters")
        name = name_str

    # Description validation & sanitization
    if description is not None:
        if len(description) > 300:
            raise HTTPException(status_code=400, detail="Description must not exceed 300 characters")
        # Sanitize to strip HTML-like characters/special symbols that could cause issue
        description = re.sub(r"[<>\";]", "", description).strip()

    # 3. File Upload Validation (Size & Magic Bytes MIME check)
    photo_bytes = None
    if photo:
        # Read the first 8 bytes for magic bytes validation
        header = await photo.read(8)
        await photo.seek(0)
        
        # Read and check total file size (limit to 5MB)
        content = await photo.read(5 * 1024 * 1024 + 1)
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Photo size exceeds maximum limit of 5MB")
        await photo.seek(0)
        
        # Validate magic bytes for JPEG or PNG
        if not (header.startswith(b'\xff\xd8\xff') or header.startswith(b'\x89PNG\r\n\x1a\n') or header.startswith(b'\x89PNG')):
            raise HTTPException(status_code=400, detail="Invalid photo type. Only JPEG and PNG are allowed.")
            
        photo_bytes = await photo.read()

    job_id = str(uuid.uuid4())

    job_store[job_id] = {
        "status": "pending",
        "progress": 0,
        "results": None,
        "error": None,
        "client_ip": client_ip
    }

    background_tasks.add_task(
        run_search_job,
        job_id=job_id,
        name=name,
        description=description,
        photo_bytes=photo_bytes
    )

    return JobStatus(job_id=job_id, status="pending", progress=0)


@router.get("/search/status/{job_id}", response_model=JobStatus)
async def get_search_status(job_id: str, request: Request):
    """Poll this endpoint to get search progress and results."""
    # 1. Rate Limiting Pass
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip, limit=60, window=60):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Maximum 60 status polls per minute.")

    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # 2. Broken Object Level Authorization (BOLA) validation
    if job.get("client_ip") and job["client_ip"] != client_ip:
        raise HTTPException(status_code=403, detail="Access denied to this job resource")

    return JobStatus(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"],
        results=job.get("results"),
        error=job.get("error")
    )
