from crewai.tools import BaseTool
from typing import List, Dict, Any
from tools.supabase_client import supabase
from tools.memory_store import MemoryStore
from langchain_openai import ChatOpenAI
from config.logging_config import setup_logging
import json
from datetime import datetime
import traceback

logger = setup_logging()
llm = ChatOpenAI(temperature=0.7)
memory_store = MemoryStore()

def generate_blog_content(trend_data: Dict[str, Any], articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate blog content based on trend analysis and articles"""
    try:
        # Extract article titles and URLs for reference
        article_refs = []
        for i, article in enumerate(articles[:5]):  # Use top 5 articles
            title = article.get('title', f'Article {i+1}')
            url = article.get('url', '')
            article_refs.append(f"{title} - {url}")
        
        article_references = "\n".join(article_refs)
        
        # Create prompt for blog generation with clearer JSON formatting instructions
        # and without the summary field which is not in our database schema
        prompt = f"""Create a comprehensive blog post based on the following trend analysis and articles:

        Trend Analysis:
        - Themes: {', '.join(trend_data.get('themes', ['Technology Trends']))}
        - Developments: {', '.join(trend_data.get('developments', ['Recent Developments']))}
        - Trends: {', '.join(trend_data.get('trends', ['Emerging Trends']))}
        - Insights: {', '.join(trend_data.get('insights', ['Key Insights']))}

        Article References:
        {article_references}

        Your blog post should include:
        1. An engaging title
        2. Well-structured content with headings
        3. Key insights and analysis
        4. Future implications

        IMPORTANT: You must format your response as a valid JSON object with the following structure:
        {{
            "title": "Your blog post title here",
            "content": "Your full blog post content here in markdown format",
            "category": "The main category of the blog post",
            "image_prompt": "A prompt for generating an image that represents the blog post"
        }}

        DO NOT include a 'summary' field in your JSON response as it's not supported by our database schema.
        Ensure your response is properly formatted as JSON with quotes around keys and values.
        """
        
        response = llm.predict(prompt)
        
        # Try to extract JSON from the response if it's not a clean JSON
        try:
            # First attempt direct parsing
            blog_data = json.loads(response)
            
            # Remove summary field if it exists to avoid database errors
            if 'summary' in blog_data:
                logger.warning("Removing 'summary' field from blog data as it's not in our schema")
                blog_data.pop('summary')
                
            return blog_data
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON, attempting to extract JSON")
            
            # Try to extract JSON from the response using regex
            import re
            json_pattern = r'({[\s\S]*})'
            match = re.search(json_pattern, response)
            
            if match:
                try:
                    extracted_json = match.group(1)
                    blog_data = json.loads(extracted_json)
                    
                    # Remove summary field if it exists
                    if 'summary' in blog_data:
                        logger.warning("Removing 'summary' field from extracted blog data")
                        blog_data.pop('summary')
                        
                    logger.info("Successfully extracted JSON from response")
                    return blog_data
                except json.JSONDecodeError:
                    logger.error("Failed to parse extracted JSON")
            
            # If all parsing attempts fail, create a structured blog post from the raw response
            logger.warning("Creating structured blog post from raw response")
            
            # Try to extract a title from the response
            title_match = re.search(r'#\s*(.*?)[\n\r]', response)
            title = title_match.group(1) if title_match else "Analysis Report"
            
            return {
                "title": title,
                "content": response,
                "category": "miscellaneous",
                "image_prompt": "A visual representation of data analysis and insights"
            }

    except Exception as e:
        logger.error(f"Error generating blog content: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "title": "Technology Trends Analysis",
            "content": "An error occurred while generating the blog content. Please try again later.",
            "category": "miscellaneous",
            "image_prompt": "Error visualization"
        }

class CreateBlogPostTool(BaseTool):
    name: str = "create_blog_post"
    description: str = "Create and save a blog post based on trend analysis"
    
    def _run(self, topic: str = None, category: str = None, trend_analysis: Dict[str, Any] = None, final_answer: str = None) -> Dict[str, Any]:
        """Run the tool with the given inputs"""
        try:
            logger.info(f"create_blog_post running with topic: {topic}, category: {category}")
            
            # If we have a final answer, use it directly
            if final_answer:
                logger.info("Using final_answer as blog content")
                title = f"{topic if topic else 'Technology'} Trends Analysis"
                content = final_answer
                
                # Create blog post directly from final answer - without summary field
                new_blog = {
                    "title": title,
                    "content": content,
                    "category": category if category else "technology",
                    "image_url": None,
                    "trend_score": 1.0,
                    "created_at": datetime.now().isoformat()
                }
                
                # Save to Supabase
                logger.info(f"Saving blog post from final answer: {title}")
                try:
                    # Check for duplicate title
                    existing = supabase.table('blogs').select('id').eq('title', title).execute()
                    if existing.data:
                        logger.warning(f"Blog post with title '{title}' already exists")
                        return {
                            "status": "duplicate",
                            "message": f"Blog post with title '{title}' already exists",
                            "blog": new_blog
                        }
                    
                    result = supabase.table('blogs').insert(new_blog).execute()
                    
                    if result.data:
                        logger.info(f"Blog post saved successfully with ID: {result.data[0]['id']}")
                        return {
                            "status": "success",
                            "message": "Blog post created successfully from final answer",
                            "blog": result.data[0]
                        }
                    else:
                        logger.error("Failed to save blog post from final answer")
                        return {
                            "status": "error",
                            "message": "Failed to save blog post from final answer",
                            "blog": new_blog
                        }
                except Exception as db_error:
                    logger.error(f"Database error saving blog post: {str(db_error)}")
                    logger.error(traceback.format_exc())
                    return {
                        "status": "error",
                        "message": f"Database error: {str(db_error)}",
                        "blog": new_blog
                    }
            
            # If we don't have trend analysis, try to fetch it
            if not trend_analysis and topic:
                logger.info(f"No trend analysis provided, fetching from Supabase for topic: {topic}")
                try:
                    # Fetch articles for this topic
                    query = supabase.table('news_articles').select('*')
                    
                    if topic:
                        query = query.ilike('title', f'%{topic}%')
                    
                    if category:
                        query = query.eq('category', category)
                        
                    result = query.order('created_at', desc=True).limit(10).execute()
                    
                    if result.data:
                        logger.info(f"Fetched {len(result.data)} articles for trend analysis")
                        articles = result.data
                        
                        # Create a simple trend analysis
                        trend_analysis = {
                            "themes": [topic],
                            "developments": ["Recent developments in " + topic],
                            "trends": ["Emerging trends in " + topic],
                            "insights": ["Key insights about " + topic],
                            "articles": articles
                        }
                    else:
                        logger.warning(f"No articles found for topic: {topic}")
                        return {
                            "status": "error",
                            "message": f"No articles found for topic: {topic}",
                            "blog": None
                        }
                except Exception as db_error:
                    logger.error(f"Database error fetching articles: {str(db_error)}")
                    logger.error(traceback.format_exc())
                    return {
                        "status": "error",
                        "message": f"Database error: {str(db_error)}",
                        "blog": None
                    }
            
            # Generate blog content
            if trend_analysis:
                articles = trend_analysis.get('articles', [])
                blog_data = generate_blog_content(trend_analysis, articles)
                
                if not blog_data:
                    logger.error("Failed to generate blog content")
                    return {
                        "status": "error",
                        "message": "Failed to generate blog content",
                        "blog": None
                    }
                
                # Calculate trend score
                trend_score = 1.0
                if articles:
                    scores = [article.get('trend_score', 1.0) for article in articles if isinstance(article, dict)]
                    if scores:
                        trend_score = sum(scores) / len(scores)
                
                # Prepare blog post data - without summary field
                new_blog = {
                    "title": blog_data.get("title", f"{topic if topic else 'Technology'} Trends Analysis"),
                    "content": blog_data.get("content"),
                    "category": blog_data.get("category", category if category else "technology"),
                    "image_url": blog_data.get("image_url"),
                    "trend_score": trend_score,
                    "created_at": datetime.now().isoformat()
                }
                
                # Check for duplicate title
                try:
                    existing = supabase.table('blogs').select('id').eq('title', new_blog['title']).execute()
                    if existing.data:
                        logger.warning(f"Blog post with title '{new_blog['title']}' already exists")
                        return {
                            "status": "duplicate",
                            "message": f"Blog post with title '{new_blog['title']}' already exists",
                            "blog": new_blog
                        }
                except Exception as db_error:
                    logger.error(f"Database error checking for duplicates: {str(db_error)}")
                    logger.error(traceback.format_exc())
                
                # Save to Supabase
                logger.info(f"Saving blog post: {new_blog['title']}")
                try:
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
                except Exception as db_error:
                    logger.error(f"Database error saving blog post: {str(db_error)}")
                    logger.error(traceback.format_exc())
                    return {
                        "status": "error",
                        "message": f"Database error: {str(db_error)}",
                        "blog": new_blog
                    }
            else:
                logger.error("No trend analysis or final answer provided")
                return {
                    "status": "error",
                    "message": "No trend analysis or final answer provided",
                    "blog": None
                }
                
        except Exception as e:
            logger.error(f"Error in create_blog_post: {str(e)}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    def _parse_input(self, inputs: Any) -> Dict[str, Any]:
        """Parse the input to extract trend_analysis, topic, category, and final_answer"""
        logger.info(f"create_blog_post received inputs type: {type(inputs)}")
        
        # Default values
        trend_analysis = None
        topic = None
        category = None
        final_answer = None
        
        # Extract raw content if inputs is a string
        if isinstance(inputs, str):
            final_answer = inputs
            logger.info(f"Extracted final_answer from string input: {final_answer[:100]}...")
        
        # Extract from dictionary inputs
        elif isinstance(inputs, dict):
            # Log all keys to help with debugging
            logger.info(f"Input keys: {list(inputs.keys())}")
            
            # Case 1: Direct final answer
            if 'final_answer' in inputs:
                final_answer = inputs.get('final_answer')
                topic = inputs.get('topic')
                category = inputs.get('category')
                logger.info(f"Found final_answer with topic: {topic}")
            
            # Case 2: Direct blog content
            elif 'title' in inputs:
                title = inputs.get('title')
                content = inputs.get('content')
                category = inputs.get('category')
                final_answer = content
                topic = title
                logger.info(f"Found direct blog content with title: {title}")
            
            # Case 3: Topic and trend analysis
            elif 'topic' in inputs:
                topic = inputs.get('topic')
                category = inputs.get('category')
                trend_analysis = inputs.get('trend_analysis')
                logger.info(f"Found topic and trend analysis: {topic}")
            
            # Case 4: Description from CrewAI
            elif 'description' in inputs:
                description = inputs.get('description')
                if isinstance(description, str):
                    final_answer = description
                    logger.info(f"Extracted final_answer from description: {final_answer[:100]}...")
                elif isinstance(description, dict):
                    trend_analysis = description
                    logger.info(f"Using description as trend analysis")
            
            # Case 5: Nested inputs from CrewAI
            elif 'inputs' in inputs and isinstance(inputs['inputs'], dict):
                nested_inputs = inputs['inputs']
                logger.info(f"Nested input keys: {list(nested_inputs.keys())}")
                
                if 'description' in nested_inputs:
                    description = nested_inputs.get('description')
                    if isinstance(description, str):
                        final_answer = description
                        logger.info(f"Extracted final_answer from nested description: {final_answer[:100]}...")
                    elif isinstance(description, dict):
                        trend_analysis = description
                        logger.info(f"Using nested description as trend analysis")
                
                elif 'topic' in nested_inputs:
                    topic = nested_inputs.get('topic')
                    category = nested_inputs.get('category')
                    trend_analysis = nested_inputs.get('trend_analysis')
                    logger.info(f"Found nested topic and trend analysis: {topic}")
                
                elif 'final_answer' in nested_inputs:
                    final_answer = nested_inputs.get('final_answer')
                    topic = nested_inputs.get('topic')
                    category = nested_inputs.get('category')
                    logger.info(f"Found nested final_answer with topic: {topic}")
            
            # Case 6: Raw output from previous task
            elif 'raw' in inputs:
                final_answer = inputs.get('raw')
                logger.info(f"Extracted final_answer from raw output: {final_answer[:100]}...")
        
        # Extract content from any string in the inputs if we still don't have content
        if not final_answer and not trend_analysis and isinstance(inputs, dict):
            for key, value in inputs.items():
                if isinstance(value, str) and len(value) > 100:  # Likely content if it's a long string
                    final_answer = value
                    logger.info(f"Extracted final_answer from long string in key {key}: {final_answer[:100]}...")
                    break
        
        return {
            "trend_analysis": trend_analysis,
            "topic": topic,
            "category": category,
            "final_answer": final_answer
        }

# Create an instance of the tool
create_blog_post = CreateBlogPostTool()
