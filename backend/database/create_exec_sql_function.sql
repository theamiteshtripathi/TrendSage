-- Create a function to execute SQL statements
-- This function needs to be created in the Supabase SQL Editor
-- It allows us to execute SQL statements from our application

CREATE OR REPLACE FUNCTION exec_sql(sql text) RETURNS void AS $$
BEGIN
  EXECUTE sql;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission to the service role
GRANT EXECUTE ON FUNCTION exec_sql(text) TO service_role;

-- Add a comment to explain the function's purpose
COMMENT ON FUNCTION exec_sql(text) IS 'Execute SQL statements with service role privileges. Use with caution.'; 