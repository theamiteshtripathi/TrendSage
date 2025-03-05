import os
import time
import openai
import traceback
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from tools.news_data_collection_tool import fetch_news
from tools.trend_analyzer_tool import analyze_trends
from tools.save_blog_post_tool import save_blog_post
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

# Specialized Agents with Clear Roles
news_collector = Agent(
    role='News Research Specialist',
    goal='Collect and validate relevant news articles',
    backstory="""Expert at finding and validating news from reliable sources.
    Specializes in categorizing content and ensuring data quality.""",
    tools=[fetch_news],
    llm=llm,
    verbose=True,
    allow_delegation=False  # This agent works independently
)

trend_analyzer = Agent(
    role='Trend Analysis Expert',
    goal='Analyze news data for emerging trends and patterns',
    backstory="""Data scientist specialized in identifying trends and patterns.
    Expert at scoring trend relevance and impact.""",
    tools=[analyze_trends],
    llm=llm,
    verbose=True,
    allow_delegation=False  # This agent works independently
)

content_creator = Agent(
    role='Content Creation Specialist',
    goal='Create engaging content from analyzed trends',
    backstory="""Professional content creator with expertise in tech writing.
    Specializes in creating engaging blog posts from trend analysis.""",
    tools=[save_blog_post],
    llm=llm,
    verbose=True,
    allow_delegation=False  # This agent works independently
)

# Task Definitions with Expected Outputs
collect_news_task = Task(
    description="""
    Research and collect news articles about {topic} in {category}.
    1. Check for existing articles first
    2. Collect new articles if needed
    3. Validate and categorize content
    4. Save to database with proper metadata
    """,
    expected_output="""
    A list of collected news articles with the following structure:
    {
        'articles': [
            {
                'title': str,
                'description': str,
                'url': str,
                'category': str,
                'source': str,
                'published_at': str
            }
        ]
    }
    """,
    agent=news_collector
)

analyze_trends_task = Task(
    description="""
    Analyze collected news to identify and score trends.
    1. Process news articles
    2. Identify key trends and patterns
    3. Calculate trend scores
    4. Update database with analysis results
    """,
    expected_output="""
    A dictionary containing analyzed articles and trend summary:
    {
        'analyzed_articles': [
            {
                'id': str,
                'title': str,
                'trend_score': float,
                'category': str
            }
        ],
        'trend_summary': str
    }
    """,
    agent=trend_analyzer,
    context=[collect_news_task]
)

create_content_task = Task(
    description="""
    Create blog post from trend analysis.
    1. Use trend analysis results
    2. Write engaging content
    3. Format with proper markdown
    4. Save to database with metadata
    """,
    expected_output="""
    A dictionary containing the created blog post:
    {
        'title': str,
        'content': str,
        'category': str,
        'trend_score': float,
        'source_articles': list,
        'status': str
    }
    """,
    agent=content_creator,
    context=[analyze_trends_task]
)

# Optimized Crew Configuration
crew = Crew(
    agents=[news_collector, trend_analyzer, content_creator],
    tasks=[collect_news_task, analyze_trends_task, create_content_task],
    process=Process.sequential,  # Tasks must be executed in order
    verbose=True,
    max_iterations=3,
    task_timeout=600
)

def execute_workflow(topic: str, category: str = None):
    """Execute the complete workflow with proper error handling"""
    try:
        # Check cache first
        if check_existing_analysis(topic, category):
            logger.info(f"Using cached analysis for {topic}")
            return get_cached_results(topic, category)
        
        # Execute crew tasks
        result = crew.kickoff({
            'topic': topic,
            'category': category or 'Miscellaneous'
        })
        
        # Ensure the result is saved to Supabase
        if isinstance(result, dict) and 'content' in result:
            try:
                # Save final blog post if not already saved
                supabase.table('blogs').insert({
                    'title': result.get('title', f"Analysis: {topic}"),
                    'content': result['content'],
                    'category': category or 'Miscellaneous',
                    'trend_score': result.get('trend_score', 1.0),
                    'status': 'published',
                    'author': 'AI Agent',
                    'published_at': 'now()'
                }).execute()
                logger.info("Final blog post saved to Supabase")
            except Exception as e:
                logger.error(f"Error saving final blog post: {str(e)}")
        
        return result
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}")
        raise

if __name__ == "__main__":
    # Test the crew
    print("Starting crew process")
    try:
        result = execute_workflow('Artificial Intelligence', 'Technology')
        print(result)
    except Exception as e:
        print(f"Error during crew process: {e}")

