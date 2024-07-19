from crewai_tools import tool
from typing import List
import mysql.connector
import os

@tool
def analyze_trends(news_data: dict) -> List[dict]:
    """
    Analyzes news data to identify trends, age groups, and popularity scores.

    Args:
        news_data (dict): The collected news articles.

    Returns:
        List[dict]: A list of identified trends with age groups and popularity scores.
    """
    # Connect to MySQL database
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME')
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT description, title, content FROM news_articles")
    articles = cursor.fetchall()
    cursor.close()
    conn.close()

    if not articles:
        raise ValueError("No articles found in news data")
    
    # Dummy implementation - replace with actual trend analysis logic
    trends = [{"trend": "AI", "age_group": "18-25", "popularity_score": 85}]
    print(f"Analyzed {len(articles)} articles and found trends: {trends}")
    return trends
