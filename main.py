from fastapi import FastAPI
from app.api.endpoints import router
from app.database.database import engine
from app.models.models import Base
from app.core.config import get_settings

# Load settings
settings = get_settings()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="UDLLM API",
    description="API for querying news articles using LLM",
    version="1.0.0"
)

# Include routers
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload during development
    )

