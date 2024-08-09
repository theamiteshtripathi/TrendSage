import os
import requests
import mysql.connector
from mysql.connector import Error
from crewai_tools import tool, ScrapeWebsiteTool
from dateutil import parser
from tools.connect_db import connect_to_db

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
def fetch_news(topic: str, language: str = 'en', max_results: int = 5) -> dict:
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
    scrape_tool = ScrapeWebsiteTool()

    for article in articles:
        # Check if the article already exists in the database
        cursor.execute("SELECT COUNT(*) FROM news_articles WHERE url = %s", (article['url'],))
        count = cursor.fetchone()[0]
        
        if count == 0:  # Only insert if the article does not exist
            try:
                # Using ScrapeWebsiteTool to scrape paragraphs ('p') from the article's URL
                scrape_tool.url = article['url']
                scrape_tool.elements = ['p']  # Targeting paragraph elements for text content
                scraped_content = scrape_tool.run()
                full_content = ' '.join([element['text'] for element in scraped_content])

            except Exception as e:
                full_content = article['content']  # Fall back to partial content if scraping fails
                print(f"Error fetching full content: {e}")
            
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
                full_content
            ))
            new_articles.append(article)

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Fetched {len(new_articles)} new articles")
    return {'articles': new_articles}
