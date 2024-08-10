import os
import time
import openai
import traceback
from openai import APIError
from crewai import Agent, Task, Crew, Process
from tools.news_data_collection_tool import fetch_news
from tools.trend_analyzer_tool import analyze_trends
from tools.save_blog_post_tool import save_blog_post
from tools.connect_db import connect_to_db

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Set OpenAI API Key and Model
openai.api_key = os.getenv('OPENAI_API_KEY')
openai_model = os.getenv('OPENAI_MODEL_NAME', 'gpt-4o-mini')  # Default to gpt-4o-mini

# Initialize tools
sql_connected = connect_to_db
fetch_news_tool = fetch_news
analyze_trends_tool = analyze_trends
save_blog_post_tool = save_blog_post

# Define agents
trend_analyzer = Agent(
    role='Trend Analyzer',
    goal='Identify trends from collected news articles using LLM',
    backstory='You are an expert in identifying trends from large datasets using the latest AI models. You utilize advanced LLMs to understand and extract meaningful insights from text data.',
    tools=[fetch_news_tool, analyze_trends_tool],
    allow_delegation=False,
    verbose=True
)

blog_writer = Agent(
    role='Blog Writer',
    goal='Write compelling blog posts based on identified trends',
    backstory='You have a knack for writing engaging and informative blog posts that captivate readers.',
    tools=[save_blog_post_tool],
    allow_delegation=False,
    verbose=True
)

# Define tasks
analyze_trends_task = Task(
    description=(
        "Analyze collected news articles to identify trends using LLM. Focus on: "
        "1. Frequency of Mentions, "
        "2. Sentiment Analysis, "
        "3. Key Entities, "
        "4. Geographical Distribution, "
        "5. Publication Date Range, "
        "6. Source Diversity, "
        "7. Emerging Keywords, "
        "8. Author Expertise, "
        "9. Industry Impact, "
        "10. Public Opinion, "
        "11. Historical Context, "
        "12. Influencer Involvement, "
        "13. Regulatory Aspects, "
        "14. Technological Implications, "
        "15. Economic Indicators, "
        "16. Visual Data, "
        "17. Quotes, "
        "18. Trend Velocity, "
        "19. Cross-Domain Connections, and "
        "20. Potential Future Developments."
    ),
    expected_output='A list of identified trends with relevant details.',
    tools=[analyze_trends_tool],
    agent=trend_analyzer,
    input_vars=['news_data'],
    output_vars=['trends']
)


analyze_trends_task = Task(
    description='Analyze collected news articles to identify trends using LLM. The analysis should focus on key AI-related trends such as Frequency of Mentions, Sentiment Analysis, Topic Modeling, and more.',
    expected_output='A list of identified trends with relevant details.',
    tools=[analyze_trends_tool],
    agent=trend_analyzer,
    input_vars=['news_data'],
    output_vars=['trends']
)

write_blog_post_task = Task(
    description='Write a blog post based on identified trends. Include age groups, popularity scores, and other relevant details.',
    expected_output='A blog post formatted in markdown.',
    tools=[save_blog_post_tool],
    agent=blog_writer,
    input_vars=['trends', 'topic']
)

# Define crew
crew = Crew(
    agents=[trend_analyzer, blog_writer],
    tasks=[fetch_news_task, analyze_trends_task, write_blog_post_task],
    process=Process.sequential
)

# Retry mechanism for crew kickoff
def retry_kickoff(crew, inputs, retries=1):
    for attempt in range(retries):
        try:
            result = crew.kickoff(inputs=inputs)
            print("Crew process finished successfully")
            return result
        except APIError as e:
            print(f"Attempt {attempt + 1} failed due to OpenAI API error: {e}")
            time.sleep(2)  # Wait before retrying
        except Exception as e:
            print(f"Attempt {attempt + 1} failed due to a different error: {e}")
            traceback.print_exc()  # This will print the full traceback
            break  # If it's a different error, break the loop and do not retry
    raise Exception("All retry attempts failed")

# Execute crew process with retries
print("Starting crew process")
try:
    result = retry_kickoff(crew, inputs={'topic': 'Artificial Intelligence'})
    print(result)
except Exception as e:
    print(f"Error during crew process: {e}")

