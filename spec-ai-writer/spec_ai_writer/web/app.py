"""
FastAPI Web Application for spec-ai-writer

Provides a modern web UI with real-time chat interface for conducting
specification interviews and managing multiple projects.
"""

import logging
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config.settings import get_settings

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="spec-ai-writer Web UI",
    description="LLM-powered interview system for generating SDD specifications",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware for React frontend
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - serves React app in production, API info in dev."""
    return {
        "app": "spec-ai-writer Web UI",
        "version": "1.0.0",
        "docs": "/api/docs",
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "llm_provider": settings.default_llm_provider
    }


# Import routers and auth
from .routers import projects, interview, specifications
from .auth import verify_api_key

# Register routers with authentication dependency
api_deps = [Depends(verify_api_key)]
app.include_router(projects.router, prefix="/api/projects", tags=["projects"], dependencies=api_deps)
app.include_router(interview.router, prefix="/api/interview", tags=["interview"], dependencies=api_deps)
app.include_router(specifications.router, prefix="/api/specs", tags=["specifications"], dependencies=api_deps)


# Static files for production build
# frontend_build_dir = Path(__file__).parent.parent.parent / "frontend" / "dist"
# if frontend_build_dir.exists():
#     app.mount("/", StaticFiles(directory=str(frontend_build_dir), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "spec_ai_writer.web.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
