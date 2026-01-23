"""
Main entry point for the shared clipboard application.
Starts the FastAPI server and hosts the frontend static files.
"""

import sys
from pathlib import Path

import uvicorn

from backend.app import app, mount_static_files


def main():
    """
    Start the application server.
    Hosts both API and frontend static files.
    """
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
    print("API documentation: http://localhost:8000/docs")
    print("Application: http://localhost:8000")
    print()

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()
