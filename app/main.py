import uvicorn
from app.app import app

if __name__ == "__main__":
    # Uvicorn configuration for development
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["./"],  # Directories to watch for changes
        log_level="info",
    )
