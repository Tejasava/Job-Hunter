"""
Main FastAPI Application
"""

import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Job Hunter Agent",
    description="AI-powered job search and application system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "AI Job Hunter Agent",
        "version": "1.0.0",
        "status": "running",
        "description": "AI-powered job search and application system"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "API is running"
    }


@app.get("/api/v1/jobs/search")
async def search_jobs(query: str, salary: int = 10, location: str = ""):
    """Search for jobs"""
    try:
        from backend.agents.global_search_agent import GlobalSearchAgent
        
        agent = GlobalSearchAgent()
        # Jobs would be searched here
        return {
            "status": "success",
            "query": query,
            "salary_bar": salary,
            "location": location,
            "jobs": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/user/profile")
async def get_user_profile(user_id: int):
    """Get user profile"""
    try:
        from backend.database.mongo import get_db
        
        db = get_db()
        profile = db.get_user_profile(user_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return {
            "status": "success",
            "profile": profile
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/applications")
async def get_applications(user_id: int):
    """Get user's job applications"""
    try:
        from backend.database.mongo import get_db
        
        db = get_db()
        applications = db.get_user_applications(user_id)
        
        return {
            "status": "success",
            "applications": applications
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/status")
async def get_system_status():
    """Get system status"""
    try:
        from backend.providers.ai_router import get_ai_router
        from backend.database.mongo import get_db
        
        ai_router = get_ai_router()
        db = get_db()
        
        available_providers = ai_router.get_available_providers()
        
        return {
            "status": "running",
            "ai_providers": available_providers,
            "database": "connected" if db.db else "offline",
            "timestamp": str(__import__('datetime').datetime.utcnow())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting AI Job Hunter Agent API...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
