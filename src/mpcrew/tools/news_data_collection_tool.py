import requests
import os
from crewai_tools import tool

@tool
def fetch_news(topic: str, language: str = 'en', max_results: int = 10) -> dict:
    """
    Fetches news articles from NewsAPI based on the given topic and language.

    Args:
        topic (str): The topic to search for news articles.
        language (str): The language of the news articles.
        max_results (int): Maximum number of articles to fetch.

    Returns:
        dict: A dictionary containing the fetched news articles.
    """
    api_key = os.getenv('NEWS_API_KEY')
    url = f"https://newsapi.org/v2/everything?q={topic}&language={language}&apiKey={api_key}&pageSize={max_results}"
    response = requests.get(url)
    print(f"Fetched {len(response.json().get('articles', []))} articles")
    return response.json()
