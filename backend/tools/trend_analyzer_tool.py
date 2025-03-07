import os
from typing import List, Dict, Any
from crewai.tools import BaseTool
from tools.supabase_client import supabase
from config.logging_config import setup_logging
from langchain_openai import ChatOpenAI
from tools.memory_store import MemoryStore
import numpy as np
from datetime import datetime, timezone
import traceback
import json

logger = setup_logging()
llm = ChatOpenAI(temperature=0.7)
memory_store = MemoryStore()

def calculate_trend_score(article_data: Dict[str, Any]) -> float:
    """Calculate trend score based on various factors"""
    base_score = 1.0
    now = datetime.now(timezone.utc).replace(tzinfo=None)  # Ensure timezone-naive
    
    # Time decay factor (newer articles score higher)
    if 'published_at' in article_data:
        try:
            # Handle ISO format with timezone
            if isinstance(article_data['published_at'], str):
                if 'Z' in article_data['published_at']:
                    # Convert to timezone-naive by removing the Z and timezone info
                    pub_date_str = article_data['published_at'].replace('Z', '')
                    pub_date = datetime.fromisoformat(pub_date_str)
                else:
                    # Already timezone-naive
                    pub_date = datetime.fromisoformat(article_data['published_at'])
            else:
                # If it's already a datetime object
                pub_date = article_data['published_at']
                
            # Ensure timezone-naive for comparison
            if pub_date.tzinfo is not None:
                pub_date = pub_date.replace(tzinfo=None)
                
            hours_old = (now - pub_date).total_seconds() / 3600
            time_factor = np.exp(-hours_old / 24)  # Exponential decay over 24 hours
        except Exception as e:
            logger.error(f"Error parsing published_at date: {e}")
            logger.error(traceback.format_exc())
            time_factor = 0.5
    else:
        time_factor = 0.5

    # Source credibility factor (can be expanded)
    source_factor = 1.0
    if article_data.get('source'):
        major_sources = {'reuters', 'associated press', 'bloomberg', 'bbc', 'cnn', 'the verge', 'wired', 'techcrunch'}
        if isinstance(article_data['source'], str) and article_data['source'].lower() in major_sources:
            source_factor = 1.2

    # Content relevance factor (based on key points)
    key_points = memory_store.get_article_key_points(article_data.get('url', ''))
    relevance_factor = min(1.5, 0.8 + (len(key_points) * 0.1))

    final_score = base_score * time_factor * source_factor * relevance_factor
    return round(final_score, 2)

class TrendAnalyzerTool(BaseTool):
    name: str = "analyze_trends"
    description: str = "Analyze trends in collected news articles"
    
    def _run(self, topic: str = None, category: str = None, articles: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run the trend analysis with the given inputs"""
        try:
            logger.info(f"analyze_trends running with topic: {topic}, category: {category}")
            
            if not articles:
                # Fetch articles from Supabase if not provided
                logger.info("No articles provided, fetching from Supabase")
                
                try:
                    query = supabase.table('news_articles').select('*')
                    
                    if topic:
                        query = query.ilike('title', f'%{topic}%')
                    
                    if category:
                        query = query.eq('category', category)
                        
                    # Order by created_at instead of updated_at
                    result = query.order('created_at', desc=True).limit(20).execute()
                    
                    if result.data:
                        logger.info(f"Fetched {len(result.data)} articles from Supabase")
                        articles = result.data
                    else:
                        logger.warning("No articles found in Supabase")
                        return {
                            "trends": [],
                            "articles": [],
                            "category": category if category else 'miscellaneous',
                            "error": "No articles found for analysis"
                        }
                except Exception as db_error:
                    logger.error(f"Database error in analyze_trends: {str(db_error)}")
                    logger.error(traceback.format_exc())
                    return {
                        "trends": [],
                        "articles": [],
                        "category": category if category else 'miscellaneous',
                        "error": str(db_error)
                    }
            
            # Process articles and calculate trend scores
            processed_articles = []
            for article in articles:
                if not isinstance(article, dict):
                    logger.warning(f"Skipping non-dict article: {type(article)}")
                    continue
                    
                # Calculate trend score
                try:
                    trend_score = calculate_trend_score(article)
                    article_with_score = article.copy()
                    article_with_score['trend_score'] = trend_score
                    processed_articles.append(article_with_score)
                except Exception as e:
                    logger.error(f"Error calculating trend score: {str(e)}")
                    logger.error(traceback.format_exc())
                    # Still include the article but with default score
                    article_with_score = article.copy()
                    article_with_score['trend_score'] = 1.0
                    processed_articles.append(article_with_score)
            
            if not processed_articles:
                logger.warning("No valid articles to analyze")
                return {
                    "trends": [],
                    "articles": [],
                    "category": category if category else 'miscellaneous',
                    "error": "No valid articles to analyze"
                }
            
            # Extract titles and content for analysis
            titles = [article.get('title', '') for article in processed_articles if article.get('title')]
            contents = [article.get('content', '') for article in processed_articles if article.get('content')]
            
            # Combine titles and content for analysis
            analysis_text = "\n\n".join(titles + contents)
            
            # Use LLM to identify trends
            prompt = f"""Analyze the following news articles to identify key trends, patterns, and insights:

            Articles:
            {analysis_text}

            Identify:
            1. Main themes across the articles
            2. Key developments or announcements
            3. Emerging trends
            4. Important insights or implications

            Format your response as a JSON with these keys:
            - themes: List of main themes
            - developments: List of key developments
            - trends: List of emerging trends
            - insights: List of important insights or implications
            """
            
            try:
                response = llm.predict(prompt)
                try:
                    trend_data = json.loads(response)
                except json.JSONDecodeError:
                    logger.error("Failed to parse LLM response as JSON")
                    # Create a structured format from unstructured response
                    trend_data = {
                        "themes": ["General Technology Trends"],
                        "developments": ["Various technology developments"],
                        "trends": [response],
                        "insights": ["Analysis based on collected articles"]
                    }
            except Exception as llm_error:
                logger.error(f"Error using LLM for trend analysis: {str(llm_error)}")
                logger.error(traceback.format_exc())
                trend_data = {
                    "themes": ["Error in trend analysis"],
                    "developments": ["Unable to process articles"],
                    "trends": ["Technical error occurred"],
                    "insights": ["Please try again later"]
                }
            
            # Sort articles by trend score
            sorted_articles = sorted(processed_articles, key=lambda x: x.get('trend_score', 0), reverse=True)
            
            # Prepare result
            result = {
                "trends": trend_data,
                "articles": sorted_articles[:10],  # Top 10 articles by trend score
                "category": category if category else 'miscellaneous',
                "topic": topic
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in analyze_trends: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "trends": [],
                "articles": [],
                "category": category if category else 'miscellaneous',
                "error": str(e)
            }
    
    def _parse_input(self, inputs: Any) -> Dict[str, Any]:
        """Parse the input to extract topic, category, and articles"""
        logger.info(f"analyze_trends received inputs type: {type(inputs)}")
        
        # Default values
        topic = None
        category = None
        articles = []
        
        # Case 1: inputs is a list (direct articles)
        if isinstance(inputs, list):
            articles = inputs
            logger.info(f"Received direct list of {len(articles)} articles")
        
        # Case 2: inputs is a dict with 'topic' key
        elif isinstance(inputs, dict) and 'topic' in inputs:
            topic = inputs.get('topic')
            category = inputs.get('category')
            articles = inputs.get('articles', [])
            logger.info(f"Received dict with topic: {topic}, category: {category}")
        
        # Case 3: inputs is a dict with 'description' key (from CrewAI)
        elif isinstance(inputs, dict) and 'description' in inputs:
            # The description might be the result from previous task
            description = inputs.get('description')
            if isinstance(description, str):
                topic = description
                logger.info(f"Extracted topic from description: {topic}")
            elif isinstance(description, list):
                articles = description
                logger.info(f"Extracted articles from description: {len(articles)} articles")
            elif isinstance(description, dict):
                articles = [description]
                logger.info(f"Extracted single article from description")
        
        # Case 4: inputs is a dict with nested 'inputs' dict (from CrewAI)
        elif isinstance(inputs, dict) and 'inputs' in inputs and isinstance(inputs['inputs'], dict):
            nested_inputs = inputs['inputs']
            logger.info(f"Nested input keys: {list(nested_inputs.keys())}")
            
            if 'description' in nested_inputs:
                description = nested_inputs.get('description')
                if isinstance(description, str):
                    topic = description
                    logger.info(f"Extracted topic from nested description: {topic}")
                elif isinstance(description, list):
                    articles = description
                    logger.info(f"Extracted articles from nested description: {len(articles)} articles")
                elif isinstance(description, dict):
                    articles = [description]
                    logger.info(f"Extracted single article from nested description")
            elif 'topic' in nested_inputs:
                topic = nested_inputs.get('topic')
                category = nested_inputs.get('category')
                articles = nested_inputs.get('articles', [])
                logger.info(f"Extracted from nested inputs - topic: {topic}, category: {category}")
            elif 'articles' in nested_inputs:
                articles = nested_inputs.get('articles', [])
                logger.info(f"Extracted articles from nested inputs: {len(articles)} articles")
        
        # Case 5: inputs is a string (direct topic)
        elif isinstance(inputs, str):
            topic = inputs
            logger.info(f"Received direct string topic: {topic}")
        
        # If we still don't have articles or topic, try to extract from any key
        if not articles and not topic and isinstance(inputs, dict):
            for key, value in inputs.items():
                if isinstance(value, list) and len(value) > 0:
                    articles = value
                    logger.info(f"Extracted articles from key {key}: {len(articles)} articles")
                    break
                elif isinstance(value, str) and len(value) > 3:
                    topic = value
                    logger.info(f"Extracted topic from key {key}: {topic}")
                    break
        
        return {
            "topic": topic,
            "category": category,
            "articles": articles
        }

# Create an instance of the tool
analyze_trends = TrendAnalyzerTool()
