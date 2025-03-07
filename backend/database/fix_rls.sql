-- This script only fixes RLS policies for the workflow_cache table
-- It doesn't touch other tables to avoid conflicts

-- Drop existing policies for workflow_cache only
DROP POLICY IF EXISTS "Public read access for workflow_cache" ON public.workflow_cache;
DROP POLICY IF EXISTS "Enable insert for service role" ON public.workflow_cache;
DROP POLICY IF EXISTS "Enable update for service role" ON public.workflow_cache;
DROP POLICY IF EXISTS "Allow all inserts to workflow_cache" ON public.workflow_cache;
DROP POLICY IF EXISTS "Allow all updates to workflow_cache" ON public.workflow_cache;

-- Create new policies with proper permissions
DO $$
BEGIN
    -- Check if the policy exists before creating it
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'workflow_cache' AND policyname = 'Public read access for workflow_cache'
    ) THEN
        EXECUTE 'CREATE POLICY "Public read access for workflow_cache" ON public.workflow_cache
                FOR SELECT USING (true)';
    END IF;

    -- Allow inserts without user authentication check
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'workflow_cache' AND policyname = 'Allow all inserts to workflow_cache'
    ) THEN
        EXECUTE 'CREATE POLICY "Allow all inserts to workflow_cache" ON public.workflow_cache
                FOR INSERT WITH CHECK (true)';
    END IF;

    -- Allow updates without user authentication check
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'workflow_cache' AND policyname = 'Allow all updates to workflow_cache'
    ) THEN
        EXECUTE 'CREATE POLICY "Allow all updates to workflow_cache" ON public.workflow_cache
                FOR UPDATE USING (true)';
    END IF;
END
$$;

-- Grant permissions to the service role
GRANT ALL ON public.workflow_cache TO service_role;
GRANT ALL ON public.workflow_cache TO anon;
GRANT ALL ON public.workflow_cache TO authenticated;

-- Refresh the schema cache
NOTIFY pgrst, 'reload schema'; 