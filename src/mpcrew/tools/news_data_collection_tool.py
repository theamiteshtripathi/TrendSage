# tools/news_data_collection_tool.py
import requests
import os
import mysql.connector
from mysql.connector import Error
from crewai_tools import tool
from dateutil import parser

def connect_to_db():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME')
        )
        return conn
    except Error as err:
        print(f"Error connecting to database: {err}")
        raise

@tool
def fetch_news(topic: str, language: str = 'en', max_results: int = 10) -> dict:
    """
    Fetches news articles from NewsAPI based on the given topic and language and stores them in the database.

    Args:
        topic (str): The topic to search for news articles.
        language (str): The language of the news articles.
        max_results (int): Maximum number of articles to fetch.

    Returns:
        dict: A dictionary containing the fetched news articles.
    """
    api_key = os.getenv('NEWS_API_KEY')
    url = f"https://newsapi.org/v2/everything?q={topic}&language={language}&pageSize={max_results}&apiKey={api_key}"
    response = requests.get(url)
    articles = response.json().get('articles', [])

    conn = connect_to_db()
    cursor = conn.cursor()

    new_articles = []
    for article in articles:
        # Check if the article already exists in the database
        cursor.execute("SELECT COUNT(*) FROM news_articles WHERE url = %s", (article['url'],))
        count = cursor.fetchone()[0]
        
        if count == 0:  # Only insert if the article does not exist
            published_at = parser.parse(article['publishedAt']).strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute("""
                INSERT INTO news_articles (source, author, title, description, url, url_to_image, published_at, content)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                article['source']['name'], 
                article['author'], 
                article['title'], 
                article['description'], 
                article['url'], 
                article['urlToImage'], 
                published_at, 
                article['content']
            ))
            new_articles.append(article)

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Fetched {len(new_articles)} new articles")
    return {'articles': new_articles}
