import os
import sys
import json
import traceback
from dotenv import load_dotenv
import openai
from supabase import create_client, Client

# Add parent directory to path to import from config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.logging_config import setup_logging
from tools.supabase_client import supabase

# Initialize logger
logger = setup_logging()

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
openai_model = os.getenv('OPENAI_MODEL_NAME', 'gpt-4o')

# Categories
CATEGORIES = ["Tech", "Business", "Health", "Science", "Sports", "Entertainment", "Politics", "Miscellaneous"]

def classify_blog_category(title, content):
    """
    Use OpenAI to classify the blog post into one of the predefined categories
    """
    try:
        # Truncate content to avoid token limits
        truncated_content = content[:1000] + "..." if len(content) > 1000 else content
        
        prompt = f"""
        Classify the following blog post into one of these categories:
        {', '.join(CATEGORIES)}
        
        Title: {title}
        Content: {truncated_content}
        
        Return ONLY the category name, nothing else.
        """
        
        response = openai.chat.completions.create(
            model=openai_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that classifies blog posts into categories."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=20
        )
        
        category = response.choices[0].message.content.strip()
        
        # Ensure the category is valid
        if category not in CATEGORIES:
            # Find the closest match
            for valid_category in CATEGORIES:
                if valid_category.lower() in category.lower():
                    return valid_category
            return "Miscellaneous"
        
        return category
    
    except Exception as e:
        logger.error(f"Error classifying blog: {str(e)}")
        return "Miscellaneous"

def update_blog_category(blog_id, category):
    """
    Update the category of a blog post in the database
    """
    try:
        response = supabase.table('blogs').update({"category": category}).eq('id', blog_id).execute()
        return response
    except Exception as e:
        logger.error(f"Error updating blog category: {str(e)}")
        return None

def categorize_all_blogs():
    """
    Categorize all blogs in the database
    """
    try:
        # Get all blogs
        response = supabase.table('blogs').select('*').execute()
        blogs = response.data
        
        logger.info(f"Found {len(blogs)} blogs to categorize")
        
        for blog in blogs:
            # Skip if already has a valid category
            if blog.get('category') in CATEGORIES:
                logger.info(f"Blog {blog['id']} already has category: {blog['category']}")
                continue
            
            # Classify the blog
            category = classify_blog_category(blog['title'], blog['content'])
            logger.info(f"Classified blog {blog['id']} as {category}")
            
            # Update the blog category
            update_response = update_blog_category(blog['id'], category)
            if update_response:
                logger.info(f"Updated blog {blog['id']} category to {category}")
            else:
                logger.error(f"Failed to update blog {blog['id']} category")
        
        logger.info("Blog categorization completed")
        
    except Exception as e:
        logger.error(f"Error in categorize_all_blogs: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    logger.info("Starting blog categorization script")
    categorize_all_blogs()
    logger.info("Blog categorization script completed") 