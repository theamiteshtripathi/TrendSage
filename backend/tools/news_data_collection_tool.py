import os
from crewai.tools import BaseTool
from newsapi import NewsApiClient
from supabase import create_client, Client
from pydantic import BaseModel, Field
from dateutil import parser
from bs4 import BeautifulSoup
import requests
from typing import Optional, List, Dict, Any
from tools.supabase_client import supabase
from tools.memory_store import MemoryStore
from config.logging_config import setup_logging
import traceback
import time
from datetime import datetime

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
        'technology': {'tech', 'technology', 'ai', 'software', 'hardware', 'digital', 'computer', 'internet', 'app', 'artificial intelligence'},
        'culture': {'culture', 'art', 'music', 'film', 'entertainment', 'movie', 'tv', 'television', 'book', 'literature'},
        'business': {'business', 'economy', 'finance', 'market', 'stock', 'investment', 'company', 'startup', 'entrepreneur'},
        'fashion': {'fashion', 'style', 'clothing', 'design', 'trend', 'wear', 'apparel', 'luxury', 'brand'},
        'sports': {'sports', 'game', 'athlete', 'football', 'basketball', 'soccer', 'tennis', 'baseball', 'olympics'},
        'politics': {'politics', 'government', 'policy', 'election', 'president', 'congress', 'senate', 'law', 'vote'},
        'health': {'health', 'medical', 'wellness', 'healthcare', 'disease', 'medicine', 'doctor', 'hospital', 'fitness'}
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
        logger.error(traceback.format_exc())
        return ""

# Define a custom tool class that inherits from BaseTool
class FetchNewsTool(BaseTool):
    name: str = "fetch_news"
    description: str = "Fetch news articles about a specific topic and save them to Supabase"
    
    def _run(self, topic: str = None, category: str = None, max_results: int = 10) -> List[Dict[Any, Any]]:
        """Run the tool with the given inputs"""
        logger.info(f"fetch_news received inputs - topic: {topic}, category: {category}")
        
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
            try:
                existing = supabase.table('news_articles')\
                    .select('*')\
                    .ilike('title', f'%{topic}%')\
                    .eq('category', category)\
                    .order('created_at', desc=True)\
                    .limit(max_results)\
                    .execute()

                if existing.data:
                    logger.info(f"Found {len(existing.data)} cached articles")
                    return existing.data
            except Exception as db_error:
                logger.error(f"Database error checking cache: {str(db_error)}")
                logger.error(traceback.format_exc())

            # Fetch from NewsAPI with exponential backoff
            max_retries = 3
            retry_delay = 1
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"Fetching from NewsAPI (attempt {attempt+1}/{max_retries})")
                    news_response = newsapi.get_everything(
                        q=topic,
                        language='en',
                        sort_by='relevancy',
                        page_size=max_results
                    )
                    
                    if not news_response['articles']:
                        logger.warning(f"No articles found for topic: {topic}")
                        return []
                    
                    break  # Success, exit retry loop
                except Exception as api_error:
                    logger.error(f"NewsAPI error (attempt {attempt+1}): {str(api_error)}")
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        logger.error("Max retries reached, giving up")
                        return []

            saved_articles = []
            for article in news_response['articles']:
                try:
                    # Check for duplicate URL
                    url_check = supabase.table('news_articles')\
                        .select('id')\
                        .eq('url', article['url'])\
                        .execute()
                    
                    if url_check.data:
                        logger.info(f"Skipping duplicate article: {article['title']}")
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
                        'content': full_content[:500],  # Truncate content for storage
                        'analyzed': False,
                        'created_at': datetime.now().isoformat(),
                        'user_id': None,
                        'category': category,
                        'trend_score': 1,
                        'image_url': None
                    }
                    
                    # Save to Supabase
                    result = supabase.table('news_articles').insert(new_article).execute()
                    if result.data:
                        saved_articles.append(result.data[0])
                        logger.info(f"Saved article: {article['title']}")
                except Exception as article_error:
                    logger.error(f"Error processing article: {str(article_error)}")
                    logger.error(traceback.format_exc())
                    continue  # Skip this article and continue with the next one
            
            logger.info(f"Saved {len(saved_articles)} new articles")
            return saved_articles
            
        except Exception as e:
            logger.error(f"Error in fetch_news: {str(e)}")
            logger.error(traceback.format_exc())
            return []

    def _parse_input(self, inputs: Any) -> Dict[str, Any]:
        """Parse the input to extract topic, category, and max_results"""
        logger.info(f"Parsing inputs type: {type(inputs)}")
        
        # Default values
        topic = None
        category = None
        max_results = 10
        
        # Case 1: inputs is a string (direct topic)
        if isinstance(inputs, str):
            topic = inputs
            logger.info(f"Parsed direct string topic: {topic}")
        
        # Case 2: inputs is a dict with 'topic' key
        elif isinstance(inputs, dict) and 'topic' in inputs:
            topic = inputs.get('topic')
            category = inputs.get('category')
            max_results = inputs.get('max_results', 10)
            logger.info(f"Parsed dict with topic: {topic}, category: {category}")
        
        # Case 3: inputs is a dict with 'description' key (from CrewAI)
        elif isinstance(inputs, dict) and 'description' in inputs:
            description = inputs.get('description')
            if isinstance(description, str):
                topic = description
                logger.info(f"Extracted topic from description: {topic}")
        
        # Case 4: inputs is a dict with nested 'inputs' dict (from CrewAI)
        elif isinstance(inputs, dict) and 'inputs' in inputs and isinstance(inputs['inputs'], dict):
            nested_inputs = inputs['inputs']
            logger.info(f"Nested input keys: {list(nested_inputs.keys())}")
            
            if 'description' in nested_inputs:
                description = nested_inputs.get('description')
                if isinstance(description, str):
                    topic = description
                    logger.info(f"Extracted topic from nested description: {topic}")
            elif 'topic' in nested_inputs:
                topic = nested_inputs.get('topic')
                category = nested_inputs.get('category')
                max_results = nested_inputs.get('max_results', 10)
                logger.info(f"Extracted from nested inputs - topic: {topic}, category: {category}")
        
        # If we still don't have a topic, try to extract from any string in the inputs
        if not topic and isinstance(inputs, dict):
            for key, value in inputs.items():
                if isinstance(value, str) and len(value) > 3:
                    topic = value
                    logger.info(f"Extracted topic from key {key}: {topic}")
                    break
        
        return {
            "topic": topic,
            "category": category,
            "max_results": max_results
        }

# Create an instance of the tool
fetch_news = FetchNewsTool()
