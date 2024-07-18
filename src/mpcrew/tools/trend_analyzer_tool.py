from crewai_tools import tool
from typing import List

@tool
def analyze_trends(news_data: dict) -> List[dict]:
    """
    Analyzes news data to identify trends, age groups, and popularity scores.

    Args:
        news_data (dict): The collected news articles.

    Returns:
        List[dict]: A list of identified trends with age groups and popularity scores.
    """
    articles = news_data.get('articles', [])
    if not articles:
        raise ValueError("No articles found in news data")
    
    # Dummy implementation - replace with actual trend analysis logic
    trends = [{"trend": "AI", "age_group": "18-25", "popularity_score": 85}]
    print(f"Analyzed {len(articles)} articles and found trends: {trends}")
    return trends
