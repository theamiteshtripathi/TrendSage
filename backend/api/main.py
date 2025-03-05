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
from crew import trend_analyzer, content_creator, crew, execute_workflow
from datetime import datetime

# Initialize logger
logger = setup_logging()

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Pydantic models
class TrendAnalysisRequest(BaseModel):
    topic: str
    category: Optional[str] = None
    max_results: Optional[int] = 10

class BlogPost(BaseModel):
    title: str
    content: str
    category: str
    image_url: Optional[str] = None

class NewsArticle(BaseModel):
    title: str
    description: str
    url: str
    category: str
    image_url: Optional[str] = None

# Predefined categories
CATEGORIES = ["All", "Tech", "Culture", "Business", "Fashion", "Sports", "Politics", "Health", "Miscellaneous"]

app = FastAPI(
    title="MPCrew API",
    description="API for MPCrew News Analysis and Blog Generation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL here
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

logger.info("FastAPI application initialized")

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to MPCrew API",
        "docs": "/docs",
        "endpoints": {
            "analyze_trends": "/api/analyze-trends",
            "blogs": "/api/blogs",
            "trends": "/api/trends",
            "categories": "/api/categories"
        }
    }

@app.get("/api/categories")
async def get_categories():
    """Get all available categories"""
    logger.info("Categories endpoint accessed")
    return {"categories": CATEGORIES}

@app.post("/api/analyze-trends")
async def analyze_trends(request: TrendAnalysisRequest):
    """Analyze trends for a given topic"""
    logger.info(f"Analyzing trends for topic: {request.topic}", 
               extra={'category': request.category})
    
    try:
        # Use CrewAI crew to analyze trends
        crew_result = execute_workflow(
            topic=request.topic,
            category=request.category
        )
        
        # Extract content from the crew result
        if isinstance(crew_result, dict):
            result = crew_result  # Use the result directly if it's already structured
        else:
            # Create structured result from string output
            content = str(crew_result)
            result = {
                'title': f"Trends in {request.topic}",
                'summary': content[:500],
                'content': content,
                'category': request.category or 'Miscellaneous',
                'analyzed': True
            }
        
        return result
    except Exception as e:
        logger.error(f"Error analyzing trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/blogs")
async def get_blogs(category: Optional[str] = None):
    """Get all blog posts, optionally filtered by category"""
    logger.info("Fetching blog posts", extra={'category': category})
    
    try:
        query = supabase.table('blogs').select('*')
        if category and category.lower() != 'all':
            query = query.eq('category', category)
        
        response = query.execute()
        return response.data
    except Exception as e:
        logger.error(f"Error fetching blogs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trends")
async def get_trends(category: Optional[str] = None):
    """Get all trends, optionally filtered by category"""
    logger.info("Fetching trends", extra={'category': category})
    
    try:
        query = supabase.table('news_articles').select('*').eq('analyzed', True)
        if category and category.lower() != 'all':
            query = query.eq('category', category)
        
        response = query.execute()
        return response.data
    except Exception as e:
        logger.error(f"Error fetching trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 