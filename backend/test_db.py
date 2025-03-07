#!/usr/bin/env python3
"""
Database testing script for MPCrew
Run this script to test database connectivity and schema validation
"""

from database.init_db import initialize_database, get_table_counts
from config.logging_config import setup_logging
import sys
import json

logger = setup_logging()

def test_database_connection():
    """Test database connection and schema validation"""
    logger.info("Testing database connection and schema")
    
    # Check if all required tables exist
    if initialize_database():
        logger.info("✅ Database schema validation successful")
        print("✅ Database schema validation successful")
        
        # Get table record counts
        table_counts = get_table_counts()
        logger.info(f"Table record counts: {json.dumps(table_counts, indent=2)}")
        
        print("\nTable record counts:")
        for table, count in table_counts.items():
            print(f"  - {table}: {count} records")
        
        return True
    else:
        logger.error("❌ Database schema validation failed")
        print("❌ Database schema validation failed")
        print("Please check the logs for more details")
        return False

if __name__ == "__main__":
    print("\n=== MPCrew Database Test ===\n")
    success = test_database_connection()
    print("\n============================\n")
    
    if not success:
        sys.exit(1) 