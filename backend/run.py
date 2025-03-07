import uvicorn
from api.main import app
from config.logging_config import setup_logging
from database.init_db import initialize_database, get_table_counts
import sys
import time

# Configure logging
logger = setup_logging()

def main():
    """Main application entry point with improved error handling"""
    logger.info("Starting MPCrew application")
    
    # Initialize database with retry logic
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            if initialize_database():
                logger.info("Database initialization successful")
                # Log table record counts for monitoring
                table_counts = get_table_counts()
                for table, count in table_counts.items():
                    logger.info(f"Table {table} has {count} records")
                break
            else:
                logger.error(f"Database initialization failed (attempt {attempt+1}/{max_retries})")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error("Max retries reached, exiting application")
                    sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error during database initialization: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                logger.error("Max retries reached, exiting application")
                sys.exit(1)
    
    # Start the FastAPI application
    try:
        logger.info("Starting FastAPI server")
        uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
    except Exception as e:
        logger.error(f"Error starting FastAPI server: {str(e)}")
        sys.exit(1)
    finally:
        logger.info("Application shutdown")

if __name__ == "__main__":
    main() 