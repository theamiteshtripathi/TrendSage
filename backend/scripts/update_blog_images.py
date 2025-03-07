import os
import sys
import requests
import traceback
from typing import List, Dict, Any

# Add parent directory to path to import from config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.logging_config import setup_logging
from tools.supabase_client import supabase
from tools.image_fetcher import get_image_for_blog, FALLBACK_IMAGES
import random

# Initialize logger
logger = setup_logging()

def is_image_url_valid(url: str) -> bool:
    """Check if an image URL is valid and accessible"""
    if not url:
        return False
    
    try:
        response = requests.head(url, timeout=5)
        content_type = response.headers.get('Content-Type', '')
        return response.status_code == 200 and content_type.startswith('image/')
    except Exception as e:
        logger.error(f"Error checking image URL {url}: {str(e)}")
        return False

def get_fallback_image(category: str) -> str:
    """Get a fallback image for a category"""
    category_key = category.capitalize()
    if category_key in FALLBACK_IMAGES:
        return random.choice(FALLBACK_IMAGES[category_key])
    return random.choice(FALLBACK_IMAGES["Miscellaneous"])

def update_blog_images() -> None:
    """Update blog posts with valid image URLs"""
    try:
        # Get all blogs
        response = supabase.table('blogs').select('*').execute()
        blogs = response.data
        
        logger.info(f"Found {len(blogs)} blogs to check")
        
        updated_count = 0
        for blog in blogs:
            blog_id = blog.get('id')
            current_image_url = blog.get('image_url')
            
            # Check if the current image URL is valid
            if current_image_url and is_image_url_valid(current_image_url):
                logger.info(f"Blog {blog_id} already has a valid image URL")
                continue
            
            # Get a new image URL
            title = blog.get('title', '')
            content = blog.get('content', '')
            category = blog.get('category', 'Miscellaneous')
            
            try:
                # Try to get an image from our image fetcher
                new_image_url = get_image_for_blog(title, content, category)
                
                # If that fails, use a fallback image
                if not new_image_url or not is_image_url_valid(new_image_url):
                    new_image_url = get_fallback_image(category)
                
                # Update the blog post
                update_response = supabase.table('blogs').update({"image_url": new_image_url}).eq('id', blog_id).execute()
                
                if update_response:
                    logger.info(f"Updated blog {blog_id} with new image URL: {new_image_url}")
                    updated_count += 1
                else:
                    logger.error(f"Failed to update blog {blog_id}")
            
            except Exception as e:
                logger.error(f"Error updating blog {blog_id}: {str(e)}")
                traceback.print_exc()
        
        logger.info(f"Updated {updated_count} blog posts with new image URLs")
        
    except Exception as e:
        logger.error(f"Error in update_blog_images: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    logger.info("Starting blog image update script")
    update_blog_images()
    logger.info("Blog image update script completed") 