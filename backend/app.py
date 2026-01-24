"""
FastAPI application for shared clipboard service.
"""

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from backend.middleware import RequestSizeLimitMiddleware, SecurityHeadersMiddleware
from backend.routes import router

# Create FastAPI app
app = FastAPI(
    title="Shared Clipboard API",
    description="Real-time shared clipboard service",
    version="0.1.0",
    docs_url=None,  # Disable docs in production
    redoc_url=None,  # Disable redoc in production
    openapi_url=None,  # Disable OpenAPI schema in production
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


# Custom rate limit handler with proper type annotation
async def rate_limit_handler(request: Request, exc: Exception) -> Response:
    """Handle rate limit exceptions."""
    return await _rate_limit_exceeded_handler(request, exc)  # type: ignore


app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
app.add_middleware(SlowAPIMiddleware)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS configuration
allowed_origins = [
    "http://localhost:25510",  # Development
    "https://localhost:8000",  # Development HTTPS
]

# Add production domain if set
production_domain = os.getenv("ALLOWED_DOMAIN")
if production_domain:
    allowed_origins.append(f"https://{production_domain}")
    # Add trusted host middleware in production
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[
            production_domain,
            f"*.{production_domain}",
            "localhost",
            "127.0.0.1",
            "0.0.0.0",
        ],
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Request size limit middleware
app.add_middleware(RequestSizeLimitMiddleware)

# Include routes
app.include_router(router)


def mount_static_files(frontend_dist_path: Path) -> None:
    """
    Mount frontend static files and setup catch-all route for SPA.
    Should be called after frontend is built.
    """
    if not frontend_dist_path.exists():
        print(f"Warning: Frontend dist directory not found at {frontend_dist_path}")
        return

    # Mount static files
    app.mount("/assets", StaticFiles(directory=frontend_dist_path / "assets"), name="assets")

    # Catch-all route for SPA (must be last)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str) -> FileResponse:
        """Serve frontend SPA for all non-API routes."""
        # Check if file exists in dist
        file_path = frontend_dist_path / full_path
        if file_path.is_file():
            return FileResponse(file_path)

        # Otherwise serve index.html for SPA routing
        return FileResponse(frontend_dist_path / "index.html")
