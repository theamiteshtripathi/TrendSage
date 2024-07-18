import requests
from crewai_tools import tool

@tool
def fetch_news(topic: str, language: str = 'en') -> dict:
    """
    Fetches news articles from NewsAPI based on the given topic and language.

    Args:
        topic (str): The topic to search for news articles.
        language (str): The language of the news articles.

    Returns:
        dict: A dictionary containing the fetched news articles.
    """
    api_key = os.getenv('NEWS_API_KEY')
    url = f"https://newsapi.org/v2/everything?q={topic}&language={language}&apiKey={api_key}"
    response = requests.get(url)
    return response.json()
