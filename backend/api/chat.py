from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from tools.rag_tool import rag_tool
from config.logging_config import setup_logging

logger = setup_logging()
router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    blog_id: str
    query: str
    chat_history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    answer: str
    context: Optional[Dict[str, Any]] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_with_blog(request: ChatRequest):
    """
    Chat with a blog post using RAG
    """
    try:
        logger.info(f"Chat request for blog ID: {request.blog_id}, query: {request.query}")
        
        # Convert chat history to the format expected by the RAG tool
        chat_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.chat_history
        ]
        
        # Call the RAG tool
        result = rag_tool._run(
            query=request.query,
            blog_id=request.blog_id,
            chat_history=chat_history
        )
        
        if "error" in result:
            logger.error(f"Error in RAG tool: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
        
        return ChatResponse(
            answer=result.get("answer", "I couldn't generate an answer."),
            context=result.get("context")
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 