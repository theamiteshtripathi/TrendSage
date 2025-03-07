from tools.supabase_client import supabase
from config.logging_config import setup_logging

logger = setup_logging()

def check_function():
    try:
        # Try to call the function with dummy data
        result = supabase.rpc(
            'match_blog_embeddings', 
            {
                'query_embedding': [0.1] * 1536,
                'match_threshold': 0.5,
                'match_count': 5
            }
        ).execute()
        
        print("Function exists!")
        print(f"Result: {result.data}")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    check_function() 