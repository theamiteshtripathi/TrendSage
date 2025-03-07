from fastapi import APIRouter
from api import trends, blogs, categories, chat

router = APIRouter()

router.include_router(trends.router, prefix="/api", tags=["trends"])
router.include_router(blogs.router, prefix="/api", tags=["blogs"])
router.include_router(categories.router, prefix="/api", tags=["categories"])
router.include_router(chat.router, prefix="/api", tags=["chat"]) 