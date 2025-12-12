"""
FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import cv_router, job_router, writer_router, supervisor_router
from app.services.session_manager import get_session_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup: Initialize services
    print("\n" + "="*70)
    print("Starting JobWriterAI API...")
    print("="*70 + "\n")
    yield
    # Shutdown: Cleanup
    print("\nShutting down JobWriterAI API...")


app = FastAPI(
    title="JobWriterAI API",
    description="AI-powered resume and cover-letter optimization with human-in-the-loop feedback",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js frontend
        "http://localhost:5173",  # Vite frontend (if using)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(cv_router)
app.include_router(job_router)
app.include_router(writer_router)
app.include_router(supervisor_router)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "JobWriterAI API",
        "status": "running",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "agents": {
            "cv": "/api/cv",
            "job": "/api/job",
            "writer": "/api/writer",
            "supervisor": "/api/supervisor"
        }
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    session_manager = get_session_manager()
    
    return {
        "status": "healthy",
        "version": "0.1.0",
        "agents": {
            "cv_agent": "operational",
            "job_agent": "operational",
            "writer_agent": "operational",
            "supervisor_agent": "operational"
        },
        "active_sessions": session_manager.get_session_count(),
        "endpoints": {
            "cv": "/api/cv",
            "job": "/api/job",
            "writer": "/api/writer",
            "supervisor": "/api/supervisor"
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)