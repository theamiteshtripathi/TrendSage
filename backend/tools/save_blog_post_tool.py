import os
from crewai.tools import tool
from supabase import create_client, Client
from datetime import datetime

@tool("Save Blog Post Tool")
async def save_blog_post(title: str, content: str, topic: str) -> dict:
    """Saves a generated blog post to the database."""
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )
    
    try:
        # Prepare blog post data
        data = {
            'title': title,
            'content': content,
            'topic': topic,
            'published_at': datetime.utcnow().isoformat(),
            'status': 'published'
        }
        
        # Insert into Supabase
        result = supabase.table('blogs').insert(data).execute()
        
        if result.data:
            return {
                'status': 'success',
                'message': 'Blog post saved successfully',
                'post_id': result.data[0]['id']
            }
        else:
            return {
                'status': 'error',
                'message': 'Failed to save blog post',
                'post_id': None
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'post_id': None
        }
