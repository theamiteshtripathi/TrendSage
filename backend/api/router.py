from fastapi import APIRouter
from api import chat

router = APIRouter()

# Only include the chat router since other endpoints are defined in main.py
router.include_router(chat.router, prefix="/api", tags=["chat"]) 