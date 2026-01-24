"""
API routes for clipboard operations.
"""

import asyncio

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.auth import create_access_token, get_current_user, verify_password, verify_token
from backend.models import ClipboardData, LoginRequest, LoginResponse, UpdateRequest
from backend.storage import storage

# Create router
router = APIRouter()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.post("/api/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(request: Request, data: LoginRequest):
    """
    Authenticate user with password and return JWT token.
    Rate limited to 5 attempts per minute per IP.
    """
    client_ip = request.client.host if request.client else "unknown"
    print(f"[Security] Login attempt from IP: {client_ip}")

    if not verify_password(data.password):
        print(f"[Security] Login FAILED from IP: {client_ip}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    print(f"[Security] Login SUCCESS from IP: {client_ip}")
    token = create_access_token({"sub": "user"})
    return LoginResponse(token=token)


@router.get("/api/clipboard", response_model=ClipboardData)
@limiter.limit("30/minute")
async def get_clipboard(request: Request, user: dict = Depends(get_current_user)):
    """
    Get current clipboard content (requires authentication).
    Rate limited to 30 requests per minute per user.
    """
    content = await storage.get_content()
    return ClipboardData(content=content)


@router.post("/api/clipboard")
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


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = ""):
    """
    WebSocket endpoint for real-time clipboard synchronization.
    Requires valid JWT token as query parameter.
    Rate limited and logged for security monitoring.

    Note: Token is passed via query parameter due to browser WebSocket API
    limitations. Ensure HTTPS is used in production.
    """
    client_ip = websocket.client.host if websocket.client else "unknown"
    print(f"[Security] WebSocket connection attempt from IP: {client_ip}")

    # Verify token before accepting connection
    if not token or len(token) < 10 or not verify_token(token):
        print(f"[Security] WebSocket authentication FAILED from IP: {client_ip}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    print(f"[Security] WebSocket connection ESTABLISHED from IP: {client_ip}")
    await websocket.accept()
    storage.add_client(websocket)

    # Track messages for rate limiting
    message_count = 0
    last_reset_time = asyncio.get_event_loop().time()

    try:
        # Send current content immediately
        content = await storage.get_content()
        await websocket.send_json({"content": content})

        # Listen for updates from this client
        while True:
            data = await websocket.receive_json()

            # Simple rate limiting: max 30 messages per minute
            current_time = asyncio.get_event_loop().time()
            if current_time - last_reset_time >= 60:
                message_count = 0
                last_reset_time = current_time

            message_count += 1
            if message_count > 30:
                await websocket.send_json({"error": "Rate limit exceeded"})
                await asyncio.sleep(1)  # Slow down aggressive clients
                continue

            # Validate message format
            if not isinstance(data, dict) or "content" not in data:
                await websocket.send_json({"error": "Invalid message format"})
                continue

            content = data["content"]
            if not isinstance(content, str):
                await websocket.send_json({"error": "Content must be a string"})
                continue

            # Validate content length
            if len(content) > 1024 * 1024:  # 1MB limit
                await websocket.send_json({"error": "Content too large (max 1MB)"})
                continue

            await storage.set_content(content)

    except WebSocketDisconnect:
        print(f"[Security] WebSocket disconnected from IP: {client_ip}")
    except Exception as e:
        print(f"[Security] WebSocket error from IP {client_ip}: {type(e).__name__}: {e}")
    finally:
        storage.remove_client(websocket)
