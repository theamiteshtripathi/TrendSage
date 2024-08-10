import traceback
import os  # Ensure os is imported here
import openai  # Ensure the latest OpenAI library is imported
from crewai_tools import tool
from typing import List
import mysql.connector
from collections import Counter
import re
from tools.connect_db import connect_to_db
import tiktoken

@tool
def analyze_trends(news_data: dict) -> List[dict]:
    """
    Analyzes news data using GPT-4o-mini to identify AI-related trends.

    Args:
        news_data (dict): The collected news articles.

    Returns:
        List[dict]: A list of identified trends with age groups and popularity scores.
    """
    try:
        conn = connect_to_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT description, title, content FROM news_articles")
        articles = cursor.fetchall()
        cursor.close()
        conn.close()

        if not articles:
            raise ValueError("No articles found in news data")

        # Combine the text data from description, title, and content fields
        combined_text = " ".join([article['description'] + " " + article['title'] + " " + article['content'] for article in articles])

        # Tokenize the text to handle the token limit
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(combined_text)

        # Split the tokens into chunks that fit within the model's context window
        max_tokens_per_chunk = 4096  # Adjust based on your model's context window
        chunks = [tokens[i:i + max_tokens_per_chunk] for i in range(0, len(tokens), max_tokens_per_chunk)]

        # Use the GPT-4o-mini model to analyze the trends
        openai.api_key = os.getenv('OPENAI_API_KEY')
        client = openai.Client()  # Initialize the OpenAI client

        trends = []
        for chunk in chunks:
            chunk_text = encoding.decode(chunk)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a trend analysis expert. Analyze the following text data and identify trends "
                            "related to AI based on the following parameters: Frequency of Mentions, Sentiment Analysis, "
                            "Topic Modeling, Geographical Distribution, Industry Impact, Corporate Activity, "
                            "Regulatory and Ethical Issues, Research and Development, Public Figures & Thought Leaders, "
                            "Market Trends, Challenges and Risks, Public Opinion, Funding and Investments, Global Competitiveness, "
                            "and Patent Activity. Provide the analysis in a structured format."
                        )
                    },
                    {
                        "role": "user",
                        "content": chunk_text
                    }
                ]
            )

            # Correctly access the response content
            gpt_response = response.choices[0].message.content
            #print(f"LLM Response: {gpt_response}")  # For debugging

            # Assuming the response is structured, parse it into a list of trends
            chunk_trends = [{"trend": trend.strip()} for trend in gpt_response.split("\n") if trend.strip()]
            trends.extend(chunk_trends)

        print(f"Analyzed {len(articles)} articles and found trends: {trends}")
        return trends

    except Exception as e:
        print(f"Error occurred: {e}")
        traceback.print_exc()
        raise
