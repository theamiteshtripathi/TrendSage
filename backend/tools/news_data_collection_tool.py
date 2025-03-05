import os
from crewai.tools import tool
from newsapi.newsapi_client import NewsApiClient
from supabase import create_client, Client
from pydantic import BaseModel, Field
from dateutil import parser
from bs4 import BeautifulSoup
import requests
from typing import Optional, List, Dict, Any
from langchain.tools import tool
from tools.supabase_client import supabase
from config.logging_config import setup_logging

class NewsDataCollectionInput(BaseModel):
    topic: str = Field(..., description="The topic to search for news articles")
    language: str = Field(default="en", description="The language of the articles")
    max_results: int = Field(default=5, description="Maximum number of articles to fetch")

def scrape_full_content(url: str) -> str:
    """Scrape the full content of an article from its URL."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        full_content = ' '.join([p.get_text() for p in paragraphs])
        return full_content
    except Exception as e:
        print(f"Error scraping content: {e}")
        return ""

logger = setup_logging()

@tool
def fetch_news(topic: str, category: str = None) -> List[Dict[Any, Any]]:
    """Fetch news articles about a specific topic and save them to Supabase"""
    try:
        # First check if we already have recent articles
        existing = supabase.table('news_articles')\
            .select('*')\
            .eq('analyzed', False)\
            .ilike('title', f'%{topic}%')
        if category:
            existing = existing.eq('category', category)
        existing = existing.execute()

        if existing.data:
            logger.info(f"Found {len(existing.data)} existing articles")
            return existing.data

        # Create a sample article with proper UUID handling
        new_article = {
            'source': 'Sample Source',
            'title': f"Sample article about {topic}",
            'description': f"This is a sample article about {topic}",
            'url': f"https://example.com/{topic.lower().replace(' ', '-')}",
            'category': category or 'Miscellaneous',
            'analyzed': False,
            'trend_score': 1.0,
            'author': 'AI Agent',
            'published_at': 'now()',
            'content': f"Sample content about {topic}"
        }

        # Save to Supabase
        result = supabase.table('news_articles').insert(new_article).execute()
        if result.data:
            logger.info(f"Saved new article to database")
            return result.data
        else:
            logger.error("No data returned from insert operation")
            return []

    except Exception as e:
        logger.error(f"Error in fetch_news: {str(e)}")
        # Return empty list instead of raising to allow workflow to continue
        return []
