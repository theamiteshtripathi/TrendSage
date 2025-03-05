import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def get_supabase_client() -> Client:
    """Initialize and return Supabase client"""
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        raise ValueError("Supabase URL and key must be set in environment variables")
    
    return create_client(url, key)

# Initialize Supabase client
supabase: Client = get_supabase_client() 