"""
File Path: main.py

Main Entry Point for Document Vision System.

This module initializes the FastAPI application, mounts API routers for authentication,
admin, and user endpoints, and registers exception handlers.

Usage:
- Run: `python main.py`
- Access endpoints:
  - Register: `POST /api/v1/auth/register`
  - Login: `POST /api/v1/auth/login`
  - Admin: `GET /api/v1/admin/users/{user_id}`
"""

from contextlib import asynccontextmanager

from app.api.v1 import api_v1_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.db.models.user import Base
from app.db.session import db_manager
from app.utils.logging import AppLogger
from fastapi import FastAPI
from sqlalchemy import create_engine

# Configure logging
logger = AppLogger(logger_name="main").get_logger()

# Database engine for schema creation
engine = create_engine(settings.DATABASE_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events."""
    try:
        Base.metadata.create_all(bind=engine)  # Create tables if they don’t exist
        await db_manager.startup()
        logger.info("Application started with database schema initialized.")
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise
    yield
    try:
        await db_manager.shutdown()
        logger.info("Application shut down.")
    except Exception as e:
        logger.error(f"Shutdown failed: {str(e)}")


# Initialize FastAPI app
app = FastAPI(
    title=f"{settings.APP_NAME}",
    description="Transforming documents into actionable data with AI-powered clarity.",
    version="1.0.0",
    lifespan=lifespan,
)
# Include API routers
app.include_router(api_v1_router)

# Register exception handlers
register_exception_handlers(app)


# Root endpoint for testing
@app.get("/")
async def root():
    """Simple root endpoint to verify the app is running."""
    return {"message": "Welcome to the Document Vision System"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG
    )
