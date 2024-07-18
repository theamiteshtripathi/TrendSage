import os
import time
from crewai import Agent, Task, Crew, Process
from tools.news_data_collection_tool import fetch_news
from tools.trend_analyzer_tool import analyze_trends

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize tools
fetch_news_tool = fetch_news
analyze_trends_tool = analyze_trends

# Define agents
trend_analyzer = Agent(
    role='Trend Analyzer',
    goal='Identify trends from collected news articles',
    backstory='You are an expert in identifying trends from large datasets and making sense of data.',
    tools=[fetch_news_tool, analyze_trends_tool]
)

blog_writer = Agent(
    role='Blog Writer',
    goal='Write compelling blog posts based on identified trends',
    backstory='You have a knack for writing engaging and informative blog posts that captivate readers.'
)

# Define tasks
fetch_news_task = Task(
    description='Fetch news articles based on the given topic.',
    expected_output='A dictionary of news articles.',
    tools=[fetch_news_tool],
    agent=trend_analyzer
)

analyze_trends_task = Task(
    description='Analyze collected news articles to identify trends, determine age groups, and assess popularity scores.',
    expected_output='A list of identified trends with age groups and popularity scores.',
    tools=[analyze_trends_tool],
    agent=trend_analyzer
)

write_blog_post_task = Task(
    description='Write a blog post based on identified trends. Include age groups, popularity scores, and other relevant details.',
    expected_output='A blog post formatted in markdown.',
    tools=[],
    agent=blog_writer
)

# Define crew
crew = Crew(
    agents=[trend_analyzer, blog_writer],
    tasks=[fetch_news_task, analyze_trends_task, write_blog_post_task],
    process=Process.sequential
)

# Retry mechanism for crew kickoff
def retry_kickoff(crew, inputs, retries=3):
    for attempt in range(retries):
        try:
            return crew.kickoff(inputs=inputs)
        except openai.APIError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)  # Wait before retrying
    raise Exception("All retry attempts failed")

# Execute crew process with retries
print("Starting crew process")
try:
    result = retry_kickoff(crew, inputs={'topic': 'AI'})
    print("Crew process finished")
    print(result)
except Exception as e:
    print(f"Error during crew process: {e}")
