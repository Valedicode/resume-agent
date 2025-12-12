"""
FastAPI application entry point
"""

from fastapi import FastAPI
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

# CORS is handled by the frontend's rewrite proxy
# The Next.js development server (next.config.js) proxies API requests
# to this backend, so all requests appear to come from the same origin.
# This eliminates the need for CORS middleware in development and production.
#
# If you need to enable CORS for direct API access (e.g., testing with Postman),
# uncomment the following:
#
# from fastapi.middleware.cors import CORSMiddleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

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