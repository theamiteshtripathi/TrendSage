from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from mpcrew.crew import trend_analyzer, blog_writer, crew

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        # Execute the crew process
        result = crew.kickoff(inputs={'topic': request.topic})
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/blogs")
async def get_blogs():
    try:
        response = supabase.table('blogs').select('*').order('created_at', desc=True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trends")
async def get_trends():
    try:
        response = supabase.table('news_articles').select('*').eq('analyzed', True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 