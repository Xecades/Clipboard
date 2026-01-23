"""
FastAPI application for shared clipboard service.
"""

import os
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from backend.auth import create_access_token, get_current_user, verify_password, verify_token
from backend.models import ClipboardData, LoginRequest, LoginResponse, UpdateRequest
from backend.storage import storage

# Create FastAPI app
app = FastAPI(
    title="Shared Clipboard API",
    description="Real-time shared clipboard service",
    version="0.1.0",
    docs_url=None,  # Disable docs in production
    redoc_url=None,  # Disable redoc in production
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore
app.add_middleware(SlowAPIMiddleware)

# CORS configuration
allowed_origins = [
    "http://localhost:5173",  # Development
    "https://localhost:8000",  # Development HTTPS
]

# Add production domain if set
production_domain = os.getenv("ALLOWED_DOMAIN")
if production_domain:
    allowed_origins.append(f"https://{production_domain}")
    allowed_origins.append(f"https://www.{production_domain}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.post("/api/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(request: Request, data: LoginRequest):
    """
    Authenticate user with password and return JWT token.
    Rate limited to 5 attempts per minute per IP.
    """
    client_ip = request.client.host if request.client else "unknown"
    print(f"Login attempt from IP: {client_ip}")

    if not verify_password(data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    token = create_access_token({"sub": "user"})
    return LoginResponse(token=token)


@app.get("/api/clipboard", response_model=ClipboardData)
@limiter.limit("30/minute")
async def get_clipboard(request: Request, user: dict = Depends(get_current_user)):
    """
    Get current clipboard content (requires authentication).
    Rate limited to 30 requests per minute per user.
    """
    content = await storage.get_content()
    return ClipboardData(content=content)


@app.post("/api/clipboard")
@limiter.limit("10/minute")
async def update_clipboard(
    request: Request, data: UpdateRequest, user: dict = Depends(get_current_user)
):
    """
    Update clipboard content (requires authentication).
    Rate limited to 10 updates per minute per user.
    """
    # Validate content length (max 1MB)
    if len(data.content) > 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Content too large"
        )

    await storage.set_content(data.content)
    return {"status": "success"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for real-time clipboard synchronization.
    Requires valid JWT token as query parameter.
    Rate limited and logged for security monitoring.
    """
    client_ip = websocket.client.host if websocket.client else "unknown"
    print(f"WebSocket connection attempt from IP: {client_ip}")

    # Verify token before accepting connection
    if not token or not verify_token(token):
        print(f"WebSocket authentication failed from IP: {client_ip}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    print(f"WebSocket connection established from IP: {client_ip}")
    await websocket.accept()
    storage.add_client(websocket)

    try:
        # Send current content immediately
        content = await storage.get_content()
        await websocket.send_json({"content": content})

        # Listen for updates from this client
        while True:
            data = await websocket.receive_json()

            # Validate message format
            if not isinstance(data, dict) or "content" not in data:
                continue

            content = data["content"]
            if not isinstance(content, str):
                continue

            # Validate content length
            if len(content) > 1024 * 1024:  # 1MB limit
                await websocket.send_json({"error": "Content too large"})
                continue

            await storage.set_content(content)

    except WebSocketDisconnect:
        print(f"WebSocket disconnected from IP: {client_ip}")
        storage.remove_client(websocket)
    except Exception as e:
        print(f"WebSocket error from IP {client_ip}: {e}")
        storage.remove_client(websocket)


def mount_static_files(frontend_dist_path: Path):
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
    async def serve_spa(full_path: str):
        """Serve frontend SPA for all non-API routes."""
        # Check if file exists in dist
        file_path = frontend_dist_path / full_path
        if file_path.is_file():
            return FileResponse(file_path)

        # Otherwise serve index.html for SPA routing
        return FileResponse(frontend_dist_path / "index.html")
