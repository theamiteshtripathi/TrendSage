from crewai.tools import tool
from typing import List, Dict, Any
from tools.supabase_client import supabase
from tools.memory_store import MemoryStore
from langchain_openai import ChatOpenAI
from config.logging_config import setup_logging
import json
from datetime import datetime

logger = setup_logging()
llm = ChatOpenAI(temperature=0.7)
memory_store = MemoryStore()

def generate_blog_content(trend_data: Dict[str, Any], articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate a blog post from trend analysis and article data"""
    try:
        # Handle string input for trend_data
        if isinstance(trend_data, str):
            try:
                trend_info = json.loads(trend_data)
            except json.JSONDecodeError:
                trend_info = {
                    "themes": ["General Analysis"],
                    "developments": ["Based on collected articles"],
                    "trends": [trend_data],
                    "insights": ["Analysis in progress"]
                }
        else:
            trend_info = trend_data.get('trends', {})
            if isinstance(trend_info, str):
                try:
                    trend_info = json.loads(trend_info)
                except json.JSONDecodeError:
                    trend_info = {"analysis": trend_info}
        
        # Create article context safely
        article_context = "\n\n".join([
            f"Article: {article.get('title', 'Untitled')}\n"
            f"Summary: {article.get('summary', 'No summary available')}\n"
            f"Key Points: {', '.join(article.get('key_points', []))}"
            for article in articles if isinstance(article, dict)
        ])
        
        prompt = f"""Based on the following trend analysis and articles, write a comprehensive blog post:

        Trend Analysis:
        - Themes: {trend_info.get('themes', [])}
        - Developments: {trend_info.get('developments', [])}
        - Emerging Trends: {trend_info.get('trends', [])}
        - Key Insights: {trend_info.get('insights', [])}

        Source Articles:
        {article_context}

        Write a well-structured blog post that:
        1. Has an engaging title
        2. Includes an introduction that hooks the reader
        3. Discusses the main trends and their implications
        4. Provides specific examples from the source articles
        5. Concludes with insights about future implications

        Format the response as a JSON with these keys:
        - title: The blog post title
        - content: The full blog post content
        - summary: A brief summary (2-3 sentences)
        - category: The main category of the content
        - image_prompt: A detailed prompt for generating an image that represents the main theme
        """

        response = llm.predict(prompt)
        try:
            blog_data = json.loads(response)
            return blog_data
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON")
            return {
                "title": "Analysis Report",
                "content": response,
                "summary": response[:200] + "...",
                "category": "miscellaneous",
                "image_prompt": "A visual representation of data analysis and insights"
            }

    except Exception as e:
        logger.error(f"Error generating blog content: {str(e)}")
        return None

@tool
def create_blog_post(inputs) -> Dict[str, Any]:
    """Create and save a blog post based on trend analysis"""
    try:
        # Handle different input formats
        if isinstance(inputs, dict):
            trend_analysis = inputs.get('trend_analysis', {})
            topic = inputs.get('topic')
            category = inputs.get('category')
        else:
            # Legacy format
            trend_analysis = inputs
            topic = None
            category = None
            
        logger.info(f"Creating blog post for topic: {topic}, category: {category}")
        
        # If trend_analysis is not provided, fetch from Supabase
        if not trend_analysis or not isinstance(trend_analysis, dict):
            logger.info("No trend analysis provided, fetching from Supabase")
            query = supabase.table('news_articles').select('*').eq('analyzed', True)
            if topic:
                query = query.ilike('title', f'%{topic}%')
            if category:
                query = query.eq('category', category)
                
            response = query.execute()
            articles = response.data
            
            if not articles:
                logger.warning("No analyzed articles found")
                return {"error": "No analyzed articles available"}
                
            trend_analysis = {
                "articles": articles,
                "category": category or "miscellaneous"
            }
        
        # Generate blog content
        blog_data = generate_blog_content(
            trend_analysis,
            trend_analysis.get('articles', [])
        )
        
        if not blog_data:
            logger.error("Failed to generate blog content")
            return {"error": "Blog generation failed"}

        # Calculate average trend score
        trend_scores = [
            article.get('trend_score', 0)
            for article in trend_analysis.get('articles', [])
        ]
        avg_trend_score = sum(trend_scores) / len(trend_scores) if trend_scores else 0

        # Use provided category or extract from trend analysis
        final_category = (category or 
                        trend_analysis.get('category') or 
                        blog_data.get('category', 'miscellaneous')).lower()

        # Prepare blog post data
        blog_post = {
            'title': blog_data['title'],
            'content': blog_data['content'],
            'category': final_category,
            'trend_score': round(avg_trend_score, 2),
            'image_url': '',  # To be updated with actual image URL
            'source_articles': [
                article['id'] for article in trend_analysis.get('articles', [])
            ],
            'metadata': {
                'topic': topic,
                'summary': blog_data.get('summary', ''),
                'created_at': datetime.now().isoformat()
            }
        }

        # Check for duplicate title
        existing = supabase.table('blogs')\
            .select('id')\
            .eq('title', blog_post['title'])\
            .execute()

        if existing.data:
            logger.warning(f"Blog post with title '{blog_post['title']}' already exists")
            return {"error": "Duplicate blog post title"}

        # Save to Supabase
        result = supabase.table('blogs').insert(blog_post).execute()
        
        if result.data:
            logger.info(f"Successfully created blog post: {blog_post['title']}")
            return {
                "success": True,
                "blog_post": result.data[0],
                "image_prompt": blog_data.get('image_prompt', '')
            }
        else:
            logger.error("Failed to save blog post")
            return {"error": "Failed to save blog post"}

    except Exception as e:
        logger.error(f"Error in create_blog_post: {str(e)}")
        return {"error": str(e)}
