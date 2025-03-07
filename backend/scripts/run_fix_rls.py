import os
import sys
import traceback
from dotenv import load_dotenv
from supabase import create_client, Client

# Add parent directory to path to import from config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.logging_config import setup_logging

# Initialize logger
logger = setup_logging()

def run_sql_script(script_path):
    """Run a SQL script on the Supabase database using the service role key"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get Supabase credentials
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_service_key:
            logger.error("Missing Supabase credentials")
            print("ERROR: Missing Supabase credentials. Check your .env file.")
            return False
        
        if "REPLACE_WITH_ACTUAL_SERVICE_ROLE_KEY" in supabase_service_key:
            logger.error("Service role key contains placeholder text")
            print("ERROR: You need to replace the placeholder with your actual service role key.")
            print("Get it from your Supabase dashboard under Project Settings > API > service_role key")
            return False
        
        # Create Supabase client with service role key
        supabase: Client = create_client(supabase_url, supabase_service_key)
        logger.info("Supabase client initialized with service role")
        
        # Read the SQL script
        with open(script_path, 'r') as f:
            sql_script = f.read()
        
        # Split the script into statements
        statements = sql_script.split(';')
        
        # Execute each statement
        success_count = 0
        error_count = 0
        
        for statement in statements:
            statement = statement.strip()
            if not statement:
                continue
                
            try:
                # Execute the statement using the REST API
                # Note: This is a simplified approach - for complex SQL you might need
                # to use a direct PostgreSQL connection
                response = supabase.rpc('exec_sql', {'sql': statement + ';'}).execute()
                logger.info(f"Executed SQL statement successfully")
                success_count += 1
            except Exception as e:
                logger.error(f"Error executing SQL statement: {str(e)}")
                error_count += 1
                print(f"ERROR executing statement: {str(e)}")
        
        logger.info(f"SQL script execution completed: {success_count} successful, {error_count} failed")
        print(f"SQL script execution completed: {success_count} successful, {error_count} failed")
        
        # Create the exec_sql function if it doesn't exist
        if error_count > 0 and "function exec_sql does not exist" in str(e):
            print("\nThe exec_sql function doesn't exist. You need to create it first.")
            print("Please run the following SQL in the Supabase SQL Editor:")
            print("""
CREATE OR REPLACE FUNCTION exec_sql(sql text) RETURNS void AS $$
BEGIN
  EXECUTE sql;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
            """)
            print("\nAfter creating the function, run this script again.")
            
        return success_count > 0 and error_count == 0
        
    except Exception as e:
        logger.error(f"Error running SQL script: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              'database', 'fix_rls.sql')
    
    print(f"Running SQL script: {script_path}")
    if os.path.exists(script_path):
        success = run_sql_script(script_path)
        if success:
            print("SQL script executed successfully!")
        else:
            print("SQL script execution failed. Check the logs for details.")
            print("\nAlternative: Copy the SQL from fix_rls.sql and run it directly in the Supabase SQL Editor.")
    else:
        print(f"ERROR: SQL script not found at {script_path}") 