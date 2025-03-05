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

# Initialize logger
logger = setup_logging()

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Set OpenAI API Key and Model
openai.api_key = os.getenv('OPENAI_API_KEY')
openai_model = os.getenv('OPENAI_MODEL_NAME', 'gpt-4')

logger.info("Initializing CrewAI components", extra={'extra_data': {'model': openai_model}})

# Initialize the language model
llm = ChatOpenAI(
    model=openai_model,
    temperature=0.7,
    api_key=os.getenv('OPENAI_API_KEY')
)

# Define agents with tools
trend_analyzer = Agent(
    role='Trend Analyzer',
    goal='Identify trends from collected news articles using LLM',
    backstory='You are an expert in identifying trends from large datasets using the latest AI models.',
    tools=[fetch_news, analyze_trends],
    llm=llm,
    verbose=True
)

blog_writer = Agent(
    role='Blog Writer',
    goal='Write compelling blog posts based on identified trends',
    backstory='You have a knack for writing engaging and informative blog posts that captivate readers.',
    tools=[save_blog_post],
    llm=llm,
    verbose=True
)

# Define tasks with expected outputs
fetch_news_task = Task(
    description="""
        Fetch news articles based on the given topic.
        Make sure to collect relevant and recent articles.
    """,
    expected_output="""
        A list of news articles with their titles, descriptions, and content.
        Each article should be relevant to the given topic.
    """,
    agent=trend_analyzer
)

analyze_trends_task = Task(
    description="""
        Analyze collected news articles to identify trends using LLM. Focus on:
        1. Frequency of Mentions
        2. Sentiment Analysis
        3. Key Entities
        4. Geographical Distribution
        5. Emerging Technologies
        6. Market Impacts
    """,
    expected_output="""
        A structured analysis of trends including:
        - Common themes and patterns
        - Overall sentiment
        - Key stakeholders and entities
        - Geographic distribution of news
        - Emerging technologies or innovations
        - Market impacts and business implications
    """,
    agent=trend_analyzer,
    context=[fetch_news_task]
)

write_blog_post_task = Task(
    description="""
        Write a comprehensive blog post based on the identified trends.
        The post should be engaging, informative, and well-structured.
    """,
    expected_output="""
        A well-written blog post that includes:
        - Engaging introduction
        - Clear analysis of trends
        - Supporting evidence and examples
        - Actionable insights
        - Proper formatting in markdown
    """,
    agent=blog_writer,
    context=[analyze_trends_task]
)

# Define crew
crew = Crew(
    agents=[trend_analyzer, blog_writer],
    tasks=[fetch_news_task, analyze_trends_task, write_blog_post_task],
    process=Process.sequential,
    verbose=True
)

# Retry mechanism for crew kickoff
def retry_kickoff(crew, inputs, retries=1):
    try:
        logger.info("Starting crew execution", extra={'extra_data': {'inputs': inputs, 'retry_attempt': retries}})
        result = crew.kickoff(inputs)
        logger.info("Crew execution completed successfully")
        return result
    except Exception as e:
        logger.error(f"Error during crew execution: {str(e)}", 
                    extra={'extra_data': {
                        'error_type': type(e).__name__,
                        'traceback': traceback.format_exc()
                    }})
        if retries > 0:
            logger.info(f"Retrying... {retries} attempts remaining")
            time.sleep(2)  # Add a small delay before retrying
            return retry_kickoff(crew, inputs, retries - 1)
        else:
            logger.critical("Max retries reached, operation failed")
            raise e

if __name__ == "__main__":
    # Execute crew process with retries
    print("Starting crew process")
    try:
        result = retry_kickoff(crew, inputs={'topic': 'Artificial Intelligence'})
        print(result)
    except Exception as e:
        print(f"Error during crew process: {e}")

