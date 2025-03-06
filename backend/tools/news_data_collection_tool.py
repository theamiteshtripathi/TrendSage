import os
from crewai.tools import tool
from newsapi import NewsApiClient
from supabase import create_client, Client
from pydantic import BaseModel, Field
from dateutil import parser
from bs4 import BeautifulSoup
import requests
from typing import Optional, List, Dict, Any
from langchain.tools import tool
from tools.supabase_client import supabase
from tools.memory_store import MemoryStore
from config.logging_config import setup_logging

# Initialize components
logger = setup_logging()
newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))
memory_store = MemoryStore(retention_period=60)  # 60 minutes retention

VALID_CATEGORIES = {
    'technology', 'culture', 'business', 'fashion', 
    'sports', 'politics', 'health', 'miscellaneous'
}

class NewsDataCollectionInput(BaseModel):
    topic: str = Field(..., description="The topic to search for news articles")
    language: str = Field(default="en", description="The language of the articles")
    max_results: int = Field(default=5, description="Maximum number of articles to fetch")

def classify_category(topic: str, default: str = 'miscellaneous') -> str:
    """Classify topic into predefined categories"""
    topic_lower = topic.lower()
    
    category_keywords = {
        'technology': {'tech', 'technology', 'ai', 'software', 'hardware', 'digital'},
        'culture': {'culture', 'art', 'music', 'film', 'entertainment'},
        'business': {'business', 'economy', 'finance', 'market'},
        'fashion': {'fashion', 'style', 'clothing', 'design'},
        'sports': {'sports', 'game', 'athlete', 'football', 'basketball'},
        'politics': {'politics', 'government', 'policy', 'election'},
        'health': {'health', 'medical', 'wellness', 'healthcare'}
    }
    
    for category, keywords in category_keywords.items():
        if any(keyword in topic_lower for keyword in keywords):
            return category
    
    return default

def scrape_full_content(url: str) -> str:
    """Scrape the full content of an article from its URL."""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()
        
        # Get text from article body
        article = soup.find('article') or soup.find('main') or soup.body
        if article:
            paragraphs = article.find_all('p')
        else:
            paragraphs = soup.find_all('p')
        
        full_content = ' '.join([p.get_text().strip() for p in paragraphs])
        return full_content
    except Exception as e:
        logger.error(f"Error scraping content: {str(e)}")
        return ""

@tool
def fetch_news(inputs) -> List[Dict[Any, Any]]:
    """Fetch news articles about a specific topic and save them to Supabase"""
    logger.info(f"fetch_news received inputs: {inputs}")
    
    # Handle different input formats
    topic = None
    category = None
    
    # Case 1: inputs is a string (direct topic)
    if isinstance(inputs, str):
        topic = inputs
    
    # Case 2: inputs is a dict with 'topic' key
    elif isinstance(inputs, dict) and 'topic' in inputs:
        topic = inputs.get('topic')
        category = inputs.get('category')
    
    # Case 3: inputs is a dict with 'description' key (from CrewAI)
    elif isinstance(inputs, dict) and 'description' in inputs:
        topic = inputs.get('description')
    
    # Case 4: inputs is a dict with nested 'inputs' dict (from CrewAI)
    elif isinstance(inputs, dict) and 'inputs' in inputs and isinstance(inputs['inputs'], dict):
        if 'description' in inputs['inputs']:
            topic = inputs['inputs'].get('description')
        elif 'topic' in inputs['inputs']:
            topic = inputs['inputs'].get('topic')
            category = inputs['inputs'].get('category')
    
    # If we still don't have a topic, try to extract it from any string in the inputs
    if not topic and isinstance(inputs, dict):
        for key, value in inputs.items():
            if isinstance(value, str) and len(value) > 3:
                topic = value
                break
    
    if not topic:
        logger.error("No topic provided to fetch_news")
        return []
        
    logger.info(f"Processing fetch_news for topic: {topic}, category: {category}")
    
    try:
        # Determine category
        if not category or category not in VALID_CATEGORIES:
            category = classify_category(topic)
        
        logger.info(f"Fetching news for topic: {topic}, category: {category}")
        
        # Check Supabase cache first
        existing = supabase.table('news_articles')\
            .select('*')\
            .eq('analyzed', True)\
            .ilike('title', f'%{topic}%')\
            .eq('category', category)\
            .order('published_at', desc=True)\
            .limit(10)\
            .execute()

        if existing.data:
            logger.info(f"Found {len(existing.data)} cached articles")
            return existing.data

        # Fetch from NewsAPI
        news_response = newsapi.get_everything(
            q=topic,
            language='en',
            sort_by='relevancy',
            page_size=10
        )

        if not news_response['articles']:
            logger.warning(f"No articles found for topic: {topic}")
            return []

        saved_articles = []
        for article in news_response['articles']:
            # Check for duplicate URL
            url_check = supabase.table('news_articles')\
                .select('id')\
                .eq('url', article['url'])\
                .execute()
            
            if url_check.data:
                continue  # Skip if URL exists

            # Scrape full content
            full_content = scrape_full_content(article['url'])
            
            # Store in memory for analysis
            memory_store.add_article(
                article['url'], 
                full_content,
                metadata={
                    'title': article['title'],
                    'description': article['description'],
                    'category': category
                }
            )

            # Prepare article data
            new_article = {
                'source': article['source']['name'],
                'author': article['author'],
                'title': article['title'],
                'description': article['description'],
                'url': article['url'],
                'url_to_image': article['urlToImage'],
                'published_at': article['publishedAt'],
                'category': category,
                'analyzed': False,
                'trend_score': 1.0,
                'content': memory_store.get_article_summary(article['url'])
            }

            # Save to Supabase
            result = supabase.table('news_articles').insert(new_article).execute()
            if result.data:
                saved_articles.extend(result.data)

        logger.info(f"Saved {len(saved_articles)} new articles")
        return saved_articles

    except Exception as e:
        logger.error(f"Error in fetch_news: {str(e)}")
        return []
