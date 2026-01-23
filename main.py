"""
Main entry point for the shared clipboard application.
Starts the FastAPI server and hosts the frontend static files.
"""

import os
import sys
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

from backend.app import app, mount_static_files


def main():
    """
    Start the application server.
    Hosts both API and frontend static files.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Read configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    # Check if frontend is built
    frontend_dist = Path(__file__).parent / "frontend" / "dist"

    if not frontend_dist.exists():
        print("=" * 60)
        print("WARNING: Frontend not built!")
        print("Please run the following commands first:")
        print("  cd frontend")
        print("  npm install")
        print("  npm run build")
        print("=" * 60)
        print()
        response = input("Continue anyway? (y/N): ")
        if response.lower() != "y":
            sys.exit(1)
    else:
        # Mount frontend static files
        mount_static_files(frontend_dist)
        print(f"✓ Frontend loaded from: {frontend_dist}")

    # Start server
    print("\nStarting Shared Clipboard server...")
    print()

    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
