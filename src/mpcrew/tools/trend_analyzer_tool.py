import os
from crewai_tools import tool
from typing import List
import mysql.connector
from tools.connect_db import connect_to_db
from collections import Counter
import re

@tool
def analyze_trends(news_data: dict) -> List[dict]:
    """
    Analyzes news data to identify trends, age groups, and popularity scores.

    Args:
        news_data (dict): The collected news articles.

    Returns:
        List[dict]: A list of identified trends with age groups and popularity scores.
    """
    import os
    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT description, title, content FROM news_articles")
    articles = cursor.fetchall()
    cursor.close()
    conn.close()

    if not articles:
        raise ValueError("No articles found in news data")
    
    # Analyze the text to extract trends
    text_data = " ".join([article['description'] + " " + article['title'] + " " + article['content'] for article in articles])
    words = re.findall(r'\b\w+\b', text_data.lower())
    common_words = Counter(words).most_common(10)
    
    trends = [{"trend": word, "age_group": "18-25", "popularity_score": score} for word, score in common_words]
    
    print(f"Analyzed {len(articles)} articles and found trends: {trends}")
    return trends
