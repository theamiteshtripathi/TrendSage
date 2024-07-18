import os
from crewai import Agent, Task, Crew, Process
from news_data_collection_tool import fetch_news
from trend_analyzer_tool import analyze_trends

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Define agents
trend_analyzer = Agent(
    role='Trend Analyzer',
    goal='Identify trends from collected news articles',
    backstory='You are an expert in identifying trends from large datasets and making sense of data.',
    tools=[analyze_trends]
)

blog_writer = Agent(
    role='Blog Writer',
    goal='Write compelling blog posts based on identified trends',
    backstory='You have a knack for writing engaging and informative blog posts that captivate readers.'
)

# Define tasks
analyze_trends_task = Task(
    description='Analyze collected news articles to identify trends, determine age groups, and assess popularity scores.',
    expected_output='A list of identified trends with age groups and popularity scores.',
    tools=[analyze_trends],
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
    tasks=[analyze_trends_task, write_blog_post_task],
    process=Process.sequential
)

# Execute crew process
result = crew.kickoff(inputs={'topic': 'AI'})
print(result)
