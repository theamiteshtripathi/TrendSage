import os
from typing import List, Dict, Any
from langchain.tools import tool
from tools.supabase_client import supabase
from config.logging_config import setup_logging
from langchain_openai import ChatOpenAI
from tools.memory_store import MemoryStore
import numpy as np
from datetime import datetime, timedelta

logger = setup_logging()
llm = ChatOpenAI(temperature=0.7)
memory_store = MemoryStore()

def calculate_trend_score(article_data: Dict[str, Any]) -> float:
    """Calculate trend score based on various factors"""
    base_score = 1.0
    now = datetime.now()
    
    # Time decay factor (newer articles score higher)
    if 'published_at' in article_data:
        pub_date = datetime.fromisoformat(article_data['published_at'].replace('Z', '+00:00'))
        hours_old = (now - pub_date).total_seconds() / 3600
        time_factor = np.exp(-hours_old / 24)  # Exponential decay over 24 hours
    else:
        time_factor = 0.5

    # Source credibility factor (can be expanded)
    source_factor = 1.0
    if article_data.get('source'):
        major_sources = {'reuters', 'associated press', 'bloomberg', 'bbc', 'cnn'}
        if article_data['source'].lower() in major_sources:
            source_factor = 1.2

    # Content relevance factor (based on key points)
    key_points = memory_store.get_article_key_points(article_data['url'])
    relevance_factor = min(1.5, 0.8 + (len(key_points) * 0.1))

    final_score = base_score * time_factor * source_factor * relevance_factor
    return round(final_score, 2)

@tool
def analyze_trends(inputs) -> Dict[str, Any]:
    """Analyze trends in collected news articles"""
    try:
        # Handle different input formats
        if isinstance(inputs, dict):
            topic = inputs.get('topic')
            category = inputs.get('category')
            articles = inputs.get('articles', [])
        else:
            # Legacy format
            articles = inputs
            topic = None
            category = None
            
        logger.info(f"Analyzing trends for topic: {topic}, category: {category}")
        
        if not articles:
            # Fetch articles from Supabase if not provided
            query = supabase.table('news_articles').select('*').eq('analyzed', False)
            if topic:
                query = query.ilike('title', f'%{topic}%')
            if category:
                query = query.eq('category', category)
            
            response = query.execute()
            articles = response.data
            logger.info(f"Fetched {len(articles)} articles from Supabase")
            
        if not articles:
            logger.warning("No articles available for analysis")
            return {"trends": [], "articles": [], "category": category or "miscellaneous"}

        # Process articles and calculate trend scores
        article_summaries = []
        for article in articles:
            # Skip if article is not a dictionary
            if not isinstance(article, dict):
                continue

            # Get article data from memory store or directly
            article_url = article.get('url')
            if article_url and article_url in memory_store.articles:
                summary = memory_store.get_article_summary(article_url)
                key_points = memory_store.get_article_key_points(article_url)
            else:
                summary = article.get('description', '')
                key_points = []
                
            # Calculate trend score
            trend_score = calculate_trend_score(article)
            
            article_summaries.append({
                'id': article.get('id'),
                'title': article.get('title'),
                'summary': summary,
                'key_points': key_points,
                'trend_score': trend_score
            })

            # Update article in Supabase with trend score
            if article.get('id'):
                supabase.table('news_articles')\
                    .update({'trend_score': trend_score, 'analyzed': True})\
                    .eq('id', article['id'])\
                    .execute()

        # Extract overall trends using LLM
        if article_summaries:
            combined_summaries = "\n\n".join([
                f"Article: {a.get('title', 'Untitled')}\nSummary: {a.get('summary', '')}\nKey Points: {', '.join(a.get('key_points', []))}"
                for a in article_summaries
            ])
            
            prompt = f"""Analyze these articles about {topic or 'the given topic'} and identify the main trends:
            {combined_summaries}
            
            Please identify:
            1. Main themes or patterns
            2. Important developments
            3. Emerging trends
            4. Key insights
            
            Format as a JSON with these keys: themes, developments, trends, insights"""

            trend_analysis = llm.predict(prompt)
            logger.info("Completed trend analysis")
            
            return {
                "trends": trend_analysis,
                "articles": article_summaries,
                "category": category or "miscellaneous"
            }
        else:
            return {
                "trends": [],
                "articles": [],
                "category": category or "miscellaneous",
                "message": "No articles could be analyzed"
            }

    except Exception as e:
        logger.error(f"Error in analyze_trends: {str(e)}")
        return {
            "trends": [],
            "articles": [],
            "category": category or "miscellaneous",
            "error": str(e)
        }
