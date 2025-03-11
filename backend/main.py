from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import get_db

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="API for Roll Call by AI application",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection is handled by SQLAlchemy in app/db/database.py

# Include API routes
from app.api.api_v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Roll Call by AI API",
        "docs": "/docs",
        "version": "0.1.0"
    }

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    # Any startup tasks can be added here
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # Any shutdown tasks can be added here
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)