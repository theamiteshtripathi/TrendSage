from typing import Dict, Any
from langchain.tools import tool
from tools.supabase_client import supabase
from config.logging_config import setup_logging

logger = setup_logging()

@tool
def save_blog_post(trend_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Create and save a blog post based on trend analysis"""
    try:
        # Extract data from trend analysis
        articles = trend_analysis.get('analyzed_articles', [])
        summary = trend_analysis.get('trend_summary', '')
        
        if not articles:
            raise ValueError("No analyzed articles provided")

        # Create blog post
        blog_post = {
            'title': f"Trend Analysis: {articles[0]['category']}",
            'content': summary,
            'category': articles[0]['category'],
            'trend_score': max(article['trend_score'] for article in articles),
            'source_articles': articles,
            'status': 'published',
            'author': 'AI Agent',
            'published_at': 'now()'
        }

        # Save to Supabase
        result = supabase.table('blogs').insert(blog_post).execute()
        logger.info("Blog post saved successfully")
        
        return result.data[0]

    except Exception as e:
        logger.error(f"Error in save_blog_post: {str(e)}")
        raise
