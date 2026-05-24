from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import search, health
from app.core.config import settings

app = FastAPI(
    title="Zip API",
    description="Public figure intelligence search engine",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])

@app.on_event("startup")
async def startup_event():
    print("Zip API is running...")
    import asyncio
    loop = asyncio.get_event_loop()
    
    def preload_models():
        try:
            from app.services.face.face_matcher import FaceMatcher
            fm = FaceMatcher()
            fm._get_insight_app()
            print("[Startup] InsightFace models loaded successfully")
        except Exception as e:
            print(f"[Startup] InsightFace preload skipped: {e}")
        try:
            from deepface import DeepFace
            import numpy as np
            print("[Startup] DeepFace ready")
        except Exception as e:
            print(f"[Startup] DeepFace preload skipped: {e}")
    
    loop.run_in_executor(None, preload_models)
