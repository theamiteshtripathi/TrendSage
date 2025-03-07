import os
import time
import openai
import traceback
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from tools.news_data_collection_tool import fetch_news
from tools.trend_analyzer_tool import analyze_trends
from tools.save_blog_post_tool import create_blog_post
from config.logging_config import setup_logging
from tools.supabase_client import supabase
from datetime import datetime
import json
import postgrest

# Initialize logger and environment
logger = setup_logging()
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
openai_model = os.getenv('OPENAI_MODEL_NAME', 'gpt-4o')

logger.info("Initializing CrewAI components", extra={'extra_data': {'model': openai_model}})

# Initialize the language model
llm = ChatOpenAI(
    model=openai_model,
    temperature=0.7,
    api_key=os.getenv('OPENAI_API_KEY')
)

# Create singleton instances of agents
news_collector = None
trend_analyzer = None
content_creator = None

def get_news_collector():
    global news_collector
    if news_collector is None:
        news_collector = Agent(
            role='News Collector',
            goal='Collect and validate relevant news articles',
            backstory="""You are an expert news curator with a keen eye for quality sources
            and relevant content. Your job is to find and validate news articles that are
            both credible and relevant to the topic.""",
            tools=[fetch_news],
            allow_delegation=False,
            verbose=True
        )
    return news_collector

def get_trend_analyzer():
    global trend_analyzer
    if trend_analyzer is None:
        trend_analyzer = Agent(
            role='Trend Analyzer',
            goal='Analyze news articles to identify trends and patterns',
            backstory="""You are a skilled data analyst specializing in identifying trends
            and patterns in news content. Your expertise lies in extracting meaningful
            insights from large volumes of information.""",
            tools=[analyze_trends],
            allow_delegation=False,
            verbose=True
        )
    return trend_analyzer

def get_content_creator():
    global content_creator
    if content_creator is None:
        content_creator = Agent(
            role='Content Creator',
            goal='Create engaging blog posts based on trend analysis',
            backstory="""You are a skilled content creator who excels at transforming
            complex trend analysis into engaging blog posts. You know how to structure
            content for maximum impact and readability.""",
            tools=[create_blog_post],
            allow_delegation=False,
            verbose=True
        )
    return content_creator

def create_tasks(topic: str, category: str = None) -> list[Task]:
    # Get agent instances
    news_collector = get_news_collector()
    trend_analyzer = get_trend_analyzer()
    content_creator = get_content_creator()

    # Create task descriptions with the topic and category information
    news_task_description = f"""Collect news articles about {topic} in category {category if category else 'any'}.
        Ensure articles are recent and from reliable sources.
        Expected Output: List of validated news articles with full content"""
    
    analysis_task_description = f"""Analyze the collected news articles about {topic} to identify trends.
        Focus on emerging patterns, key developments, and significant insights.
        Expected Output: Detailed trend analysis with supporting evidence"""
    
    blog_task_description = f"""Create an engaging blog post based on the trend analysis of {topic}.
        Include key insights, supporting evidence, and future implications.
        Expected Output: Complete blog post with title, content, and metadata"""

    # Log the task information
    logger.info(f"Creating tasks for topic: {topic}, category: {category if category else 'miscellaneous'}")

    # Define a callback function to save the blog post
    def save_blog_callback(output):
        try:
            logger.info("Blog post creation task completed, saving to database")
            # Extract the content from the output
            content = output.raw
            
            # Use the create_blog_post tool's _run method directly
            # This avoids the 'Tool' object is not callable error
            parsed_input = create_blog_post._parse_input({
                'final_answer': content,
                'topic': topic,
                'category': category if category else 'technology'
            })
            
            result = create_blog_post._run(
                topic=parsed_input.get('topic'),
                category=parsed_input.get('category'),
                final_answer=parsed_input.get('final_answer')
            )
            
            logger.info(f"Blog post save result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in save_blog_callback: {str(e)}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}

    # Create tasks with proper context (no context for first task, previous tasks as context for subsequent tasks)
    collect_news = Task(
        description=news_task_description,
        agent=news_collector,
        expected_output="List of news articles with their content and metadata",
        async_execution=False
    )

    analyze_trends = Task(
        description=analysis_task_description,
        agent=trend_analyzer,
        expected_output="Trend analysis report with identified patterns and insights",
        context=[collect_news],  # Use the previous task as context
        async_execution=False,
        output_required=True
    )

    create_blog = Task(
        description=blog_task_description,
        agent=content_creator,
        expected_output="Published blog post with trend analysis and insights",
        context=[analyze_trends],  # Only use the trend analysis task as context to avoid confusion
        async_execution=False,
        output_required=True,
        callback=save_blog_callback  # Add the callback to save the blog post
    )

    logger.info(f"Created tasks for topic: {topic}, category: {category if category else 'miscellaneous'}")
    return [collect_news, analyze_trends, create_blog]

def serialize_crew_output(crew_output):
    """Convert CrewAI output to a JSON-serializable format"""
    try:
        if hasattr(crew_output, 'raw'):
            # If it's a TaskOutput object
            return {
                "raw": crew_output.raw,
                "description": crew_output.description if hasattr(crew_output, 'description') else None,
                "task_id": str(crew_output.task_id) if hasattr(crew_output, 'task_id') else None
            }
        elif isinstance(crew_output, dict):
            # If it's already a dictionary, make sure all values are serializable
            serialized_dict = {}
            for key, value in crew_output.items():
                if hasattr(value, 'raw'):
                    # Handle TaskOutput objects within the dictionary
                    serialized_dict[key] = {
                        "raw": value.raw,
                        "description": value.description if hasattr(value, 'description') else None,
                        "task_id": str(value.task_id) if hasattr(value, 'task_id') else None
                    }
                elif isinstance(value, (str, int, float, bool, type(None))):
                    # Primitive types are already serializable
                    serialized_dict[key] = value
                else:
                    # Try to convert to string for other types
                    try:
                        serialized_dict[key] = str(value)
                    except:
                        serialized_dict[key] = "Unserializable object"
            return serialized_dict
        else:
            # For other types, convert to string
            return {"result": str(crew_output)}
    except Exception as e:
        logger.error(f"Error serializing crew output: {str(e)}")
        logger.error(traceback.format_exc())
        return {"error": "Failed to serialize crew output", "message": str(e)}

def execute_workflow(topic: str, category: str = None) -> dict:
    """Execute the news analysis and blog creation workflow"""
    try:
        logger.info(f"Starting workflow for topic: {topic}, category: {category}")
        
        # Check cache first
        cached_result = get_cached_results(topic, category)
        if cached_result:
            logger.info(f"Using cached analysis for {topic}")
            return cached_result
        
        # Create and run the crew
        crew = Crew(
            agents=[
                get_news_collector(),
                get_trend_analyzer(),
                get_content_creator()
            ],
            tasks=create_tasks(topic, category),
            verbose=True,
            process=Process.sequential
        )

        # Pass inputs as a dictionary with topic and category
        inputs = {
            'topic': topic,
            'category': category if category else 'miscellaneous'
        }
        
        logger.info(f"Kicking off crew with inputs: {inputs}")
        result = crew.kickoff(inputs=inputs)
        
        # Serialize the result before caching
        serialized_result = serialize_crew_output(result)
        
        # Add metadata to the result
        final_result = {
            "topic": topic,
            "category": category if category else 'miscellaneous',
            "timestamp": datetime.now().isoformat(),
            "result": serialized_result
        }
        
        # Save the result to cache
        try:
            cache_result(topic, category, final_result)
        except Exception as cache_error:
            logger.error(f"Error caching result: {str(cache_error)}")
            logger.error(traceback.format_exc())
        
        logger.info("Workflow completed successfully")
        return final_result

    except Exception as e:
        logger.error(f"Error in workflow execution: {str(e)}")
        logger.error(traceback.format_exc())
        return {"error": str(e)}

def check_existing_analysis(topic: str, category: str = None) -> bool:
    """Check if we already have analysis for this topic"""
    try:
        # Check for existing blog posts on this topic
        query = supabase.table('blogs').select('id')
        
        if topic:
            query = query.ilike('title', f'%{topic}%')
        
        if category:
            query = query.eq('category', category)
            
        # Only consider recent posts (last 24 hours)
        yesterday = (datetime.now().isoformat().split('T')[0] + 'T00:00:00')
        query = query.gte('created_at', yesterday)
        
        result = query.execute()
        
        return len(result.data) > 0
    except Exception as e:
        logger.error(f"Error checking existing analysis: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def get_cached_results(topic: str, category: str = None):
    """Get cached results for a topic"""
    try:
        # First check the workflow_cache table
        query = supabase.table('workflow_cache').select('*')
        
        if topic:
            query = query.ilike('topic', f'%{topic}%')
        
        if category:
            query = query.eq('category', category)
            
        cache_result = query.order('created_at', desc=True).limit(1).execute()
        
        if cache_result.data:
            logger.info(f"Found cached workflow result for topic: {topic}")
            return {
                "cached": True,
                "result": cache_result.data[0]['result'],
                "timestamp": cache_result.data[0]['created_at']
            }
        
        # If no workflow cache, check for blog posts
        query = supabase.table('blogs').select('*')
        
        if topic:
            query = query.ilike('title', f'%{topic}%')
        
        if category:
            query = query.eq('category', category)
            
        blog_result = query.order('created_at', desc=True).limit(1).execute()
        
        if blog_result.data:
            logger.info(f"Found cached blog post for topic: {topic}")
            return {
                "blog": blog_result.data[0],
                "cached": True,
                "timestamp": blog_result.data[0]['created_at']
            }
        
        return None
    except Exception as e:
        logger.error(f"Error getting cached results: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def cache_result(topic: str, category: str, result: dict):
    """Cache the result of a workflow"""
    try:
        # Check if workflow_cache table exists
        try:
            # Ensure the result is JSON serializable
            serialized_result = json.dumps(result)
            json_result = json.loads(serialized_result)
            
            # Create a cache entry
            cache_entry = {
                "topic": topic,
                "category": category if category else 'miscellaneous',
                "result": json_result,
                "created_at": datetime.now().isoformat()
            }
            
            # Try to save to Supabase
            try:
                # First attempt - standard insert
                supabase.table('workflow_cache').insert(cache_entry).execute()
                logger.info(f"Cached workflow result for topic: {topic}")
            except postgrest.exceptions.APIError as api_error:
                # Check if it's an RLS policy error
                error_data = getattr(api_error, 'args', [{}])[0]
                error_code = error_data.get('code') if isinstance(error_data, dict) else None
                
                if error_code == '42501':  # RLS policy violation
                    logger.warning("RLS policy violation, attempting to use service role")
                    
                    # Try to use service role client if available
                    try:
                        from tools.supabase_admin_client import admin_supabase
                        admin_supabase.table('workflow_cache').insert(cache_entry).execute()
                        logger.info(f"Cached workflow result using admin client for topic: {topic}")
                    except ImportError:
                        logger.error("Admin Supabase client not available")
                        # Save to local file as last resort
                        cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
                        os.makedirs(cache_dir, exist_ok=True)
                        cache_file = os.path.join(cache_dir, f"{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json")
                        with open(cache_file, 'w') as f:
                            json.dump(cache_entry, f)
                        logger.info(f"Saved workflow result to local file: {cache_file}")
                else:
                    # Re-raise if it's not an RLS error
                    raise
        except Exception as e:
            logger.error(f"Error saving to workflow_cache: {str(e)}")
            logger.error(traceback.format_exc())
            
            # If the table doesn't exist or other error, save to local file
            cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
            os.makedirs(cache_dir, exist_ok=True)
            cache_file = os.path.join(cache_dir, f"{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json")
            with open(cache_file, 'w') as f:
                json.dump({
                    "topic": topic,
                    "category": category if category else 'miscellaneous',
                    "result": result,
                    "created_at": datetime.now().isoformat()
                }, f)
            logger.info(f"Saved workflow result to local file: {cache_file}")
    except Exception as e:
        logger.error(f"Error in cache_result: {str(e)}")
        logger.error(traceback.format_exc())

# Export only what's needed
__all__ = ['execute_workflow']

if __name__ == "__main__":
    # Test the crew
    print("Starting crew process")
    try:
        result = execute_workflow('Artificial Intelligence', 'Technology')
        print(result)
    except Exception as e:
        print(f"Error during crew process: {e}")

