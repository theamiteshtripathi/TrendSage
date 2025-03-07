import os
from supabase import create_client, Client
from dotenv import load_dotenv
from config.logging_config import setup_logging

# Initialize logger
logger = setup_logging()

# Load environment variables
load_dotenv()

# Get Supabase credentials
supabase_url = os.getenv('SUPABASE_URL')
supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Create Supabase client with service role key for admin access
if supabase_url and supabase_service_key:
    try:
        admin_supabase: Client = create_client(supabase_url, supabase_service_key)
        logger.info("Supabase admin client initialized with service role")
    except Exception as e:
        logger.error(f"Error initializing Supabase admin client: {str(e)}")
        admin_supabase = None
else:
    logger.warning("Supabase admin client not initialized: missing credentials")
    admin_supabase = None 