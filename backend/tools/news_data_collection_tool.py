import os
from crewai.tools import tool
from newsapi.newsapi_client import NewsApiClient
from supabase import create_client, Client
from pydantic import BaseModel, Field
from dateutil import parser
from bs4 import BeautifulSoup
import requests
from typing import Optional, List, Dict, Any

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

@tool("News Collection Tool")
async def fetch_news(topic: str) -> list:
    """Fetches news articles based on a given topic and stores them in the database."""
    newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )
    
    try:
        # Fetch news from NewsAPI
        response = newsapi.get_everything(
            q=topic,
            language='en',
            sort_by='relevancy',
            page_size=10
        )

        if response['status'] == 'ok':
            articles = response['articles']
            
            # Store articles in Supabase
            for article in articles:
                data = {
                    'title': article['title'],
                    'description': article['description'],
                    'content': article['content'],
                    'url': article['url'],
                    'published_at': article['publishedAt'],
                    'source': article['source']['name']
                }
                
                supabase.table('news_articles').insert(data).execute()
            
            return articles
        else:
            return []
            
    except Exception as e:
        print(f"Error fetching news: {str(e)}")
        return []
