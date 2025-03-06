from typing import Dict, List, Optional
import numpy as np
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from config.logging_config import setup_logging

logger = setup_logging()

class MemoryStore:
    def __init__(self, retention_period: int = 30):
        """
        Initialize memory store with retention period in minutes
        """
        self.articles: Dict[str, Dict] = {}  # URL -> article data
        self.summaries: Dict[str, str] = {}  # URL -> summary
        self.key_points: Dict[str, List[str]] = {}  # URL -> list of key points
        self.retention_period = timedelta(minutes=retention_period)
        self.llm = ChatOpenAI(temperature=0.7)
        
    def add_article(self, url: str, content: str, metadata: Dict = None):
        """
        Add article content to memory with metadata
        """
        if url in self.articles:
            logger.info(f"Article {url} already in memory")
            return

        # Create summary and extract key points
        try:
            summary = self._create_summary(content)
            key_points = self._extract_key_points(content)
            
            self.articles[url] = {
                'content': content,
                'metadata': metadata or {},
                'added_at': datetime.now(),
            }
            self.summaries[url] = summary
            self.key_points[url] = key_points
            
            logger.info(f"Added article {url} to memory")
        except Exception as e:
            logger.error(f"Error processing article {url}: {str(e)}")

    def get_article_summary(self, url: str) -> Optional[str]:
        """Get summary for a specific article"""
        return self.summaries.get(url)

    def get_article_key_points(self, url: str) -> List[str]:
        """Get key points for a specific article"""
        return self.key_points.get(url, [])

    def get_all_summaries(self) -> Dict[str, str]:
        """Get all article summaries"""
        self._cleanup_old_entries()
        return self.summaries

    def get_all_key_points(self) -> Dict[str, List[str]]:
        """Get all article key points"""
        self._cleanup_old_entries()
        return self.key_points

    def _create_summary(self, content: str, max_length: int = 200) -> str:
        """Create a concise summary of the article content"""
        try:
            prompt = f"Summarize this article in about 200 words:\n\n{content}"
            response = self.llm.predict(prompt)
            return response[:max_length]
        except Exception as e:
            logger.error(f"Error creating summary: {str(e)}")
            return ""

    def _extract_key_points(self, content: str, max_points: int = 5) -> List[str]:
        """Extract key points from the article content"""
        try:
            prompt = f"Extract {max_points} key points from this article:\n\n{content}"
            response = self.llm.predict(prompt)
            points = [point.strip() for point in response.split('\n') if point.strip()]
            return points[:max_points]
        except Exception as e:
            logger.error(f"Error extracting key points: {str(e)}")
            return []

    def _cleanup_old_entries(self):
        """Remove entries older than retention period"""
        current_time = datetime.now()
        urls_to_remove = []
        
        for url, data in self.articles.items():
            if current_time - data['added_at'] > self.retention_period:
                urls_to_remove.append(url)
        
        for url in urls_to_remove:
            self.articles.pop(url, None)
            self.summaries.pop(url, None)
            self.key_points.pop(url, None)
            
        if urls_to_remove:
            logger.info(f"Cleaned up {len(urls_to_remove)} old entries from memory") 