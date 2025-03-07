import os
import requests
import random
import logging
from typing import Dict, List, Any, Optional
from config.logging_config import setup_logging

# Initialize logger
logger = setup_logging()

# Unsplash API access key - using a demo key for now
# In production, you should use your own API key from https://unsplash.com/developers
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "demo")  # Try to get from environment or use demo

# Flag to determine if we should try Unsplash API
USE_UNSPLASH_API = UNSPLASH_ACCESS_KEY != "demo"

# Log the status
if USE_UNSPLASH_API:
    logger.info("Using Unsplash API for image fetching")
else:
    logger.info("Using fallback images only (Unsplash API not configured)")

# Fallback image URLs by category - these are reliable Unsplash images
FALLBACK_IMAGES = {
    "Tech": [
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800",
        "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800",
        "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800"
    ],
    "Technology": [
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800",
        "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800",
        "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800"
    ],
    "Business": [
        "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800",
        "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800",
        "https://images.unsplash.com/photo-1664575602554-2087b04935a5?w=800"
    ],
    "Health": [
        "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=800",
        "https://images.unsplash.com/photo-1532938911079-1b06ac7ceec7?w=800",
        "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800"
    ],
    "Science": [
        "https://images.unsplash.com/photo-1507413245164-6160d8298b31?w=800",
        "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=800",
        "https://images.unsplash.com/photo-1564325724739-bae0bd08762c?w=800"
    ],
    "Sports": [
        "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800",
        "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=800",
        "https://images.unsplash.com/photo-1535131749006-b7f58c99034b?w=800"
    ],
    "Entertainment": [
        "https://images.unsplash.com/photo-1603190287605-e6ade32fa852?w=800",
        "https://images.unsplash.com/photo-1598899134739-24c46f58b8c0?w=800",
        "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=800"
    ],
    "Politics": [
        "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=800",
        "https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=800",
        "https://images.unsplash.com/photo-1575320181282-9afab399332c?w=800"
    ],
    "Finance & Technology": [
        "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=800",
        "https://images.unsplash.com/photo-1518186285589-2f7649de83e0?w=800",
        "https://images.unsplash.com/photo-1620714223084-8fcacc6dfd8d?w=800"
    ],
    "Miscellaneous": [
        "https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=800",
        "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800",
        "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800"
    ]
}

def extract_keywords(title: str, content: str) -> List[str]:
    """Extract relevant keywords from title and content"""
    # Combine title and first 500 chars of content
    text = f"{title} {content[:500]}"
    
    # Remove common words and keep only significant ones
    common_words = [
        'the', 'and', 'or', 'of', 'to', 'in', 'for', 'with', 'on', 'at', 'from', 'by', 
        'about', 'as', 'an', 'a', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'but', 'if', 'then', 'else', 'when',
        'up', 'down', 'out', 'in', 'that', 'this', 'these', 'those', 'it', 'its'
    ]
    
    # Extract words, remove punctuation, and filter out common words
    words = text.lower().replace(r"/[^\w\s]/g", "").split()
    keywords = [word for word in words if word not in common_words and len(word) > 3]
    
    # Return unique keywords
    return list(set(keywords))[:5]  # Limit to top 5 keywords

def fetch_image_from_unsplash(query: str) -> Optional[str]:
    """Fetch an image URL from Unsplash based on the query"""
    # If we're not using the Unsplash API, return None immediately
    if not USE_UNSPLASH_API:
        return None
        
    try:
        # Unsplash API endpoint
        url = f"https://api.unsplash.com/photos/random"
        
        # Parameters
        params = {
            "query": query,
            "orientation": "landscape",
            "content_filter": "high",
        }
        
        # Headers
        headers = {
            "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
        }
        
        # Make the request
        response = requests.get(url, params=params, headers=headers, timeout=5)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            # Return the URL of the regular sized image
            return data["urls"]["regular"]
        else:
            logger.warning(f"Failed to fetch image from Unsplash: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error fetching image from Unsplash: {str(e)}")
        return None

def get_image_for_blog(title: str, content: str, category: str) -> str:
    """Get a relevant image URL for a blog post"""
    try:
        # Extract keywords from title and content
        keywords = extract_keywords(title, content)
        
        # Try to fetch an image from Unsplash using the keywords
        for keyword in keywords:
            image_url = fetch_image_from_unsplash(keyword)
            if image_url:
                logger.info(f"Found image for keyword: {keyword}")
                return image_url
        
        # If no image found with keywords, try with the category
        image_url = fetch_image_from_unsplash(category)
        if image_url:
            logger.info(f"Found image for category: {category}")
            return image_url
        
        # If still no image, use a fallback image for the category
        if category in FALLBACK_IMAGES:
            logger.info(f"Using fallback image for category: {category}")
            return random.choice(FALLBACK_IMAGES[category])
        
        # Last resort: use a miscellaneous fallback image
        logger.info("Using miscellaneous fallback image")
        return random.choice(FALLBACK_IMAGES["Miscellaneous"])
    except Exception as e:
        logger.error(f"Error getting image for blog: {str(e)}")
        return random.choice(FALLBACK_IMAGES["Miscellaneous"])

# For testing
if __name__ == "__main__":
    test_title = "The Future of Artificial Intelligence"
    test_content = "AI is transforming industries across the globe. Machine learning algorithms are becoming more sophisticated..."
    test_category = "Technology"
    
    image_url = get_image_for_blog(test_title, test_content, test_category)
    print(f"Image URL: {image_url}") 