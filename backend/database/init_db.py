from tools.supabase_client import supabase
from config.logging_config import setup_logging
import traceback

logger = setup_logging()

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    try:
        result = supabase.table(table_name).select('id').limit(1).execute()
        logger.info(f"Table validation: {table_name} exists")
        return True
    except Exception as e:
        logger.error(f"Error checking {table_name} table: {str(e)}")
        return False

def initialize_database():
    """Check and initialize database tables if they don't exist"""
    required_tables = [
        'news_articles',
        'blogs',
        'user_preferences',
        'workflow_cache'
    ]
    
    all_tables_exist = True
    
    for table in required_tables:
        if not check_table_exists(table):
            all_tables_exist = False
            logger.error(f"Required table {table} does not exist or is not accessible")
    
    if all_tables_exist:
        logger.info("Database schema validation: All required tables exist")
        return True
    else:
        logger.error("Database schema validation failed")
        logger.error("Please run the schema.sql script to create the required tables")
        return False

def get_table_counts():
    """Get counts of records in each table for monitoring"""
    tables = {
        'news_articles': 0,
        'blogs': 0,
        'user_preferences': 0,
        'workflow_cache': 0
    }
    
    try:
        for table_name in tables.keys():
            try:
                result = supabase.table(table_name).select('id', count='exact').execute()
                tables[table_name] = result.count if hasattr(result, 'count') else len(result.data)
                logger.info(f"Table {table_name} has {tables[table_name]} records")
            except Exception as e:
                logger.error(f"Error getting count for {table_name}: {str(e)}")
    except Exception as e:
        logger.error(f"Error in get_table_counts: {str(e)}")
        logger.error(traceback.format_exc())
    
    return tables

if __name__ == "__main__":
    # Run this file directly to check database initialization
    if initialize_database():
        print("Database schema is valid.")
        counts = get_table_counts()
        print("Table record counts:")
        for table, count in counts.items():
            print(f"  - {table}: {count} records")
    else:
        print("Database schema validation failed. See logs for details.") 