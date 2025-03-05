import os
from crewai.tools import tool
from supabase import create_client, Client
from langchain_openai import ChatOpenAI

@tool("Trend Analyzer Tool")
async def analyze_trends(topic: str) -> dict:
    """Analyzes trends from collected news articles using LLM."""
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )
    
    llm = ChatOpenAI(
        model=os.getenv('OPENAI_MODEL_NAME', 'gpt-4'),
        temperature=0.7,
        api_key=os.getenv('OPENAI_API_KEY')
    )
    
    try:
        # Fetch articles from Supabase
        response = supabase.table('news_articles')\
            .select('*')\
            .eq('analyzed', False)\
            .execute()
        
        articles = response.data
        
        if not articles:
            return {
                'status': 'error',
                'message': 'No new articles to analyze',
                'trends': []
            }

        # Prepare articles for analysis
        article_texts = []
        for article in articles:
            text = f"Title: {article['title']}\n"
            text += f"Description: {article['description']}\n"
            text += f"Content: {article['content']}\n"
            article_texts.append(text)

        # Analyze trends using LLM
        prompt = f"""
        Analyze the following news articles about {topic} and identify key trends.
        Focus on:
        1. Common themes and patterns
        2. Sentiment analysis
        3. Key stakeholders and entities
        4. Geographic distribution of news
        5. Emerging technologies or innovations
        6. Market impacts and business implications

        Articles:
        {'\n\n'.join(article_texts)}

        Please provide a structured analysis with specific examples and data points.
        """

        response = llm.invoke(prompt)
        analysis = response.content

        # Mark articles as analyzed
        for article in articles:
            supabase.table('news_articles')\
                .update({'analyzed': True})\
                .eq('id', article['id'])\
                .execute()

        return {
            'status': 'success',
            'message': 'Trends analyzed successfully',
            'trends': analysis
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'trends': []
        }
