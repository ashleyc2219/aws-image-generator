from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import load_configuration
from app.api.routes import create_router


def create_app():
    # Create FastAPI application
    app = FastAPI(
        title="Amazon Nova Canvas API",
        description="FastAPI service for Amazon Nova Canvas image generation capabilities",
        version="1.0.0",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Load configuration
    config = load_configuration()

    # Create and include router
    router = create_router(config)
    app.include_router(router)

    return app


app = create_app()
