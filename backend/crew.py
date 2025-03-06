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
            goal='Analyze news articles to identify emerging trends and patterns',
            backstory="""You are a data analyst specializing in trend identification and
            pattern recognition. Your expertise lies in discovering meaningful trends
            and insights from news articles.""",
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
            goal='Create engaging and informative blog posts based on trend analysis',
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

    # Create tasks with proper context (no context for first task, previous tasks as context for subsequent tasks)
    collect_news = Task(
        description=news_task_description,
        agent=news_collector,
        expected_output="List of news articles with their content and metadata"
        # First task has no context
    )

    analyze_trends = Task(
        description=analysis_task_description,
        agent=trend_analyzer,
        expected_output="Trend analysis report with identified patterns and insights",
        context=[collect_news],  # Use the previous task as context
        output_required=True
    )

    create_blog = Task(
        description=blog_task_description,
        agent=content_creator,
        expected_output="Published blog post with trend analysis and insights",
        context=[collect_news, analyze_trends],  # Use both previous tasks as context
        output_required=True
    )

    logger.info(f"Created tasks for topic: {topic}, category: {category if category else 'miscellaneous'}")
    return [collect_news, analyze_trends, create_blog]

def execute_workflow(topic: str, category: str = None) -> dict:
    """Execute the news analysis and blog creation workflow"""
    try:
        logger.info(f"Starting workflow for topic: {topic}, category: {category}")
        
        # Check cache first
        if check_existing_analysis(topic, category):
            logger.info(f"Using cached analysis for {topic}")
            return get_cached_results(topic, category)
        
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
        
        logger.info("Workflow completed successfully")
        return result

    except Exception as e:
        logger.error(f"Error in workflow execution: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"error": str(e)}

# Keep these helper functions
def check_existing_analysis(topic: str, category: str = None) -> bool:
    """Check if we already have analysis for this topic"""
    try:
        query = supabase.table('news_articles').select('*').eq('analyzed', True)
        if category:
            query = query.eq('category', category)
        query = query.ilike('title', f'%{topic}%')
        response = query.execute()
        return len(response.data) > 0
    except Exception as e:
        logger.error(f"Error checking existing analysis: {str(e)}")
        return False

def get_cached_results(topic: str, category: str = None):
    """Get cached analysis results"""
    try:
        # Get related news articles
        news_query = supabase.table('news_articles').select('*').eq('analyzed', True)
        if category:
            news_query = news_query.eq('category', category)
        news_query = news_query.ilike('title', f'%{topic}%')
        news = news_query.execute()

        # Get related blog posts
        blog_query = supabase.table('blogs').select('*')
        if category:
            blog_query = blog_query.eq('category', category)
        blog_query = blog_query.ilike('title', f'%{topic}%')
        blogs = blog_query.execute()

        return {
            'news_articles': news.data,
            'blogs': blogs.data
        }
    except Exception as e:
        logger.error(f"Error fetching cached results: {str(e)}")
        raise

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

