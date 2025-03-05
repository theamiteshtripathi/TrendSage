import os
from typing import List, Dict, Any
from langchain.tools import tool
from tools.supabase_client import supabase
from config.logging_config import setup_logging
from langchain_openai import ChatOpenAI

logger = setup_logging()

@tool
def analyze_trends(articles: List[Dict[Any, Any]]) -> Dict[str, Any]:
    """Analyze trends from the collected news articles and update their scores"""
    try:
        if not articles:
            logger.warning("No articles provided for analysis")
            return {
                'analyzed_articles': [],
                'trend_summary': 'No articles available for analysis',
                'category': 'Miscellaneous',
                'trend_score': 0.0
            }

        # Calculate trend scores (simplified example)
        analyzed_articles = []
        for article in articles:
            try:
                # Update article with trend score and mark as analyzed
                updated = supabase.table('news_articles')\
                    .update({
                        'trend_score': 1.0,  # Replace with actual scoring logic
                        'analyzed': True
                    })\
                    .eq('id', article['id'])\
                    .execute()
                
                if updated.data:
                    analyzed_articles.extend(updated.data)
            except Exception as article_error:
                logger.error(f"Error updating article {article.get('id', 'unknown')}: {str(article_error)}")
                continue
        
        # Create meaningful summary
        summary = f"Analyzed {len(analyzed_articles)} articles about {articles[0].get('category', 'various topics')}"
        
        logger.info(f"Analyzed {len(analyzed_articles)} articles")
        return {
            'analyzed_articles': analyzed_articles,
            'trend_summary': summary,
            'category': articles[0].get('category', 'Miscellaneous'),
            'trend_score': max((article.get('trend_score', 0.0) for article in analyzed_articles), default=0.0)
        }

    except Exception as e:
        logger.error(f"Error in analyze_trends: {str(e)}")
        return {
            'analyzed_articles': [],
            'trend_summary': f'Error during analysis: {str(e)}',
            'category': 'Miscellaneous',
            'trend_score': 0.0
        }
