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
        logger.info(f"create_blog_post received inputs: {inputs}")
        
        # Handle different input formats
        trend_analysis = None
        topic = None
        category = None
        title = None
        content = None
        
        # Case 1: inputs is a string (direct content)
        if isinstance(inputs, str):
            content = inputs
            title = "Technology Trends Analysis"
        
        # Case 2: inputs is a dict with specific blog content keys
        elif isinstance(inputs, dict) and 'title' in inputs:
            title = inputs.get('title')
            content = inputs.get('content')
            category = inputs.get('category', 'technology')
        
        # Case 3: inputs is a dict with 'topic' and 'trend_analysis' keys
        elif isinstance(inputs, dict) and 'topic' in inputs:
            trend_analysis = inputs.get('trend_analysis', {})
            topic = inputs.get('topic')
            category = inputs.get('category')
        
        # Case 4: inputs is a dict with 'description' key (from CrewAI)
        elif isinstance(inputs, dict) and 'description' in inputs:
            # The description might be the result from previous task
            description = inputs.get('description')
            if isinstance(description, str):
                content = description
                title = "Technology Trends Analysis"
            else:
                trend_analysis = description
        
        # Case 5: inputs is a dict with nested 'inputs' dict (from CrewAI)
        elif isinstance(inputs, dict) and 'inputs' in inputs and isinstance(inputs['inputs'], dict):
            if 'description' in inputs['inputs']:
                description = inputs['inputs'].get('description')
                if isinstance(description, str):
                    content = description
                    title = "Technology Trends Analysis"
                else:
                    trend_analysis = description
            elif 'topic' in inputs['inputs']:
                topic = inputs['inputs'].get('topic')
                category = inputs['inputs'].get('category')
                trend_analysis = inputs['inputs'].get('trend_analysis', {})
            elif 'title' in inputs['inputs']:
                title = inputs['inputs'].get('title')
                content = inputs['inputs'].get('content')
                category = inputs['inputs'].get('category', 'technology')
        
        # If we have direct title and content, use them
        if title and content:
            logger.info(f"Using provided title and content for blog post")
            blog_data = {
                "title": title,
                "content": content,
                "summary": content[:200] + "..." if len(content) > 200 else content,
                "category": category or "technology",
                "image_prompt": f"A visual representation of {title}"
            }
        # Otherwise, generate from trend analysis
        elif trend_analysis:
            logger.info(f"Generating blog content from trend analysis")
            # Fetch articles if needed for context
            articles = []
            if topic:
                query = supabase.table('news_articles')
                if category:
                    query = query.eq('category', category)
                if topic:
                    query = query.ilike('title', f'%{topic}%')
                
                result = query.limit(10).execute()
                if result.data:
                    articles = result.data
            
            # Generate blog content
            blog_data = generate_blog_content(trend_analysis, articles)
            if not blog_data:
                logger.error("Failed to generate blog content")
                return {"error": "Failed to generate blog content"}
        else:
            # Create a default blog post if no inputs are provided
            logger.warning("No valid inputs provided, creating default blog post")
            blog_data = {
                "title": "Latest Technology Trends",
                "content": "This is a placeholder for technology trend analysis. The actual content will be generated based on news analysis.",
                "summary": "Placeholder for technology trend analysis.",
                "category": "technology",
                "image_prompt": "A visual representation of technology trends"
            }
        
        # Calculate trend score
        trend_score = 1.0
        if isinstance(trend_analysis, dict) and 'articles' in trend_analysis:
            scores = [article.get('trend_score', 1.0) for article in trend_analysis['articles'] if isinstance(article, dict)]
            if scores:
                trend_score = sum(scores) / len(scores)
        
        # Prepare blog post data
        new_blog = {
            "title": blog_data.get("title"),
            "content": blog_data.get("content"),
            "summary": blog_data.get("summary", blog_data.get("content", "")[:200] + "..."),
            "category": blog_data.get("category", category or "technology"),
            "image_url": blog_data.get("image_url"),
            "trend_score": trend_score,
            "created_at": datetime.now().isoformat()
        }
        
        # Check for duplicate title
        existing = supabase.table('blogs').select('id').eq('title', new_blog['title']).execute()
        if existing.data:
            logger.warning(f"Blog post with title '{new_blog['title']}' already exists")
            return {
                "status": "duplicate",
                "message": f"Blog post with title '{new_blog['title']}' already exists",
                "blog": new_blog
            }
        
        # Save to Supabase
        logger.info(f"Saving blog post: {new_blog['title']}")
        result = supabase.table('blogs').insert(new_blog).execute()
        
        if result.data:
            logger.info(f"Blog post saved successfully with ID: {result.data[0]['id']}")
            return {
                "status": "success",
                "message": "Blog post created successfully",
                "blog": result.data[0]
            }
        else:
            logger.error("Failed to save blog post")
            return {
                "status": "error",
                "message": "Failed to save blog post",
                "blog": new_blog
            }
            
    except Exception as e:
        logger.error(f"Error in create_blog_post: {str(e)}")
        return {"error": str(e)}
