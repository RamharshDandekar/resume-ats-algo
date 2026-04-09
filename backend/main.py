from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from db import mongo_manager
from routers import candidates_router, jobs_router, matching_router, scheduler_router

# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    mongo_manager.connect(
        uri="mongodb://localhost:27017",
        db_name="intellihire"
    )
    print("✓ MongoDB connected")
    
    yield
    
    # Shutdown
    mongo_manager.disconnect()
    print("✓ MongoDB disconnected")


# Create FastAPI application
app = FastAPI(
    title="IntelliHire API",
    description="AI-Powered Resume Screening & Hiring System",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(candidates_router.router, prefix="/api/candidates", tags=["Candidates"])
app.include_router(jobs_router.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(matching_router.router, prefix="/api/matching", tags=["Skill Matching"])
app.include_router(scheduler_router.router, prefix="/api/scheduler", tags=["Interview Scheduler"])


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "IntelliHire API is running",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
