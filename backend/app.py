"""
FastAPI application for shared clipboard service.
"""

from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.auth import create_access_token, get_current_user, verify_password, verify_token
from backend.models import ClipboardData, LoginRequest, LoginResponse, UpdateRequest
from backend.storage import storage

# Create FastAPI app
app = FastAPI(
    title="Shared Clipboard API", description="Real-time shared clipboard service", version="0.1.0"
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate user with password and return JWT token.
    """
    if not verify_password(request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    token = create_access_token({"sub": "user"})
    return LoginResponse(token=token)


@app.get("/api/clipboard", response_model=ClipboardData)
async def get_clipboard(user: dict = Depends(get_current_user)):
    """
    Get current clipboard content (requires authentication).
    """
    content = await storage.get_content()
    return ClipboardData(content=content)


@app.post("/api/clipboard")
async def update_clipboard(request: UpdateRequest, user: dict = Depends(get_current_user)):
    """
    Update clipboard content (requires authentication).
    """
    await storage.set_content(request.content)
    return {"status": "success"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for real-time clipboard synchronization.
    Requires valid JWT token as query parameter.
    """
    # Verify token before accepting connection
    if not verify_token(token):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    storage.add_client(websocket)

    try:
        # Send current content immediately
        content = await storage.get_content()
        await websocket.send_json({"content": content})

        # Listen for updates from this client
        while True:
            data = await websocket.receive_json()
            if "content" in data:
                await storage.set_content(data["content"])

    except WebSocketDisconnect:
        storage.remove_client(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
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
