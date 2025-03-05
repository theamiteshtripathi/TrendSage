from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import sys
from pathlib import Path
from tools.supabase_client import supabase
from config.logging_config import setup_logging

# Initialize logger
logger = setup_logging()

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from crew import trend_analyzer, blog_writer, crew

app = FastAPI(
    title="MPCrew API",
    description="API for MPCrew News Analysis and Blog Generation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("FastAPI application initialized")

# Root endpoint
@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to MPCrew API",
        "docs": "/docs",
        "endpoints": {
            "analyze_trends": "/api/analyze-trends",
            "blogs": "/api/blogs",
            "trends": "/api/trends"
        }
    }

# Error handler for 404
@app.exception_handler(404)
async def not_found_handler(request, exc):
    logger.warning(f"Not found error for path: {request.url.path}")
    return JSONResponse(
        status_code=404,
        content={
            "message": f"Path {request.url.path} not found",
            "available_endpoints": {
                "root": "/",
                "docs": "/docs",
                "analyze_trends": "/api/analyze-trends",
                "blogs": "/api/blogs",
                "trends": "/api/trends"
            }
        }
    )

class TrendAnalysisRequest(BaseModel):
    topic: str
    language: str = "en"
    max_results: int = 5

class BlogPostResponse(BaseModel):
    id: str
    title: str
    content: str
    created_at: str

@app.post("/api/analyze-trends")
async def analyze_trends(request: TrendAnalysisRequest):
    try:
        logger.info("Starting trend analysis", 
                   extra={'extra_data': {
                       'topic': request.topic,
                       'language': request.language
                   }})
        result = trend_analyzer.analyze(request.topic, request.language, request.max_results)
        logger.info("Trend analysis completed successfully")
        return result
    except Exception as e:
        logger.error(f"Error in trend analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/blogs")
async def get_blogs():
    try:
        logger.info("Fetching blog posts")
        blogs = supabase.table("blogs").select("*").execute()
        logger.info(f"Successfully retrieved {len(blogs.data)} blog posts")
        return blogs.data
    except Exception as e:
        logger.error(f"Error fetching blogs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trends")
async def get_trends():
    try:
        logger.info("Fetching trends")
        trends = supabase.table("trends").select("*").execute()
        logger.info(f"Successfully retrieved {len(trends.data)} trends")
        return trends.data
    except Exception as e:
        logger.error(f"Error fetching trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 