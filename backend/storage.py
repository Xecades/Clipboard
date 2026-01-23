"""
Storage layer for clipboard data with file persistence.
"""

import asyncio
import json
from pathlib import Path
from typing import Optional

from fastapi import WebSocket


class ClipboardStorage:
    """
    Singleton storage for clipboard content with file persistence.
    Notifies WebSocket clients when content changes.
    """

    _instance: Optional["ClipboardStorage"] = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_initialized"):
            self._content: str = ""
            self._clients: set[WebSocket] = set()
            self._storage_path = Path("clipboard_data.json")
            self._load_from_file()
            self._initialized = True

    def _load_from_file(self):
        """Load clipboard content from file if it exists."""
        if self._storage_path.exists():
            try:
                with open(self._storage_path, encoding="utf-8") as f:
                    data = json.load(f)
                    self._content = data.get("content", "")
            except (OSError, json.JSONDecodeError):
                self._content = ""

    def _save_to_file(self):
        """Persist clipboard content to file."""
        try:
            with open(self._storage_path, "w", encoding="utf-8") as f:
                json.dump({"content": self._content}, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"Failed to save clipboard data: {e}")

    async def get_content(self) -> str:
        """Get current clipboard content."""
        async with self._lock:
            return self._content

    async def set_content(self, content: str) -> None:
        """Update clipboard content and notify all clients."""
        async with self._lock:
            self._content = content
            self._save_to_file()

        # Notify all connected WebSocket clients
        await self._broadcast(content)

    async def _broadcast(self, content: str):
        """Broadcast content update to all connected clients."""
        disconnected = set()

        for client in self._clients:
            try:
                await client.send_json({"content": content})
            except Exception:
                disconnected.add(client)

        # Remove disconnected clients
        self._clients -= disconnected

    def add_client(self, websocket: WebSocket):
        """Register a WebSocket client for updates."""
        self._clients.add(websocket)

    def remove_client(self, websocket: WebSocket):
        """Unregister a WebSocket client."""
        self._clients.discard(websocket)


# Global storage instance
storage = ClipboardStorage()
