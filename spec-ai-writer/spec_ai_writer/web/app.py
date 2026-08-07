"""
FastAPI Web Application for spec-ai-writer

Provides a modern web UI with real-time chat interface for conducting
specification interviews and managing multiple projects.
"""

import logging
from importlib.metadata import version
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware

from spec_ai_writer.config.settings import get_settings

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "connect-src 'self'; "
            "img-src 'self' data:; "
            "font-src 'self' https://fonts.gstatic.com; "
            "frame-ancestors 'none';"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


# Initialize FastAPI app
app = FastAPI(
    title="spec-ai-writer Web UI",
    description="LLM-powered interview system for generating SDD specifications",
    version=version("spec-ai-writer"),
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Security and CORS middleware
settings = get_settings()
app.add_middleware(SecurityHeadersMiddleware)
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


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "llm_provider": settings.default_llm_provider
    }


# Import routers
from .routers import projects, interview, specifications, settings as settings_router

# Register routers
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(interview.router, prefix="/api/interview", tags=["interview"])
app.include_router(specifications.router, prefix="/api/specs", tags=["specifications"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["settings"])


# Static files for production build
if settings.app_env == "production":
    frontend_build_dir = Path(__file__).parent.parent.parent / "frontend" / "dist"
    if not frontend_build_dir.exists():
        raise RuntimeError(
            "frontend/dist not found. Run `cd frontend && npm run build` first."
        )
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file = (frontend_build_dir / full_path).resolve()
        if file.is_relative_to(frontend_build_dir.resolve()) and file.is_file():
            return FileResponse(file)
        return FileResponse(frontend_build_dir / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "spec_ai_writer.web.app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
