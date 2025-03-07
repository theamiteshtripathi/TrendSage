-- This script fixes RLS policies for the workflow_cache table
-- Run this directly in the Supabase SQL Editor

-- Drop existing policies for workflow_cache only
DROP POLICY IF EXISTS "Public read access for workflow_cache" ON public.workflow_cache;
DROP POLICY IF EXISTS "Enable insert for service role" ON public.workflow_cache;
DROP POLICY IF EXISTS "Enable update for service role" ON public.workflow_cache;
DROP POLICY IF EXISTS "Allow all inserts to workflow_cache" ON public.workflow_cache;
DROP POLICY IF EXISTS "Allow all updates to workflow_cache" ON public.workflow_cache;

-- Create new policies with proper permissions
ALTER TABLE public.workflow_cache ENABLE ROW LEVEL SECURITY;

-- Public read access
CREATE POLICY "Public read access for workflow_cache" ON public.workflow_cache
    FOR SELECT USING (true);

-- Allow all operations without restrictions
CREATE POLICY "Allow all operations on workflow_cache" ON public.workflow_cache
    USING (true)
    WITH CHECK (true);

-- Grant permissions to all roles
GRANT ALL ON public.workflow_cache TO service_role;
GRANT ALL ON public.workflow_cache TO anon;
GRANT ALL ON public.workflow_cache TO authenticated;

-- Refresh the schema cache
NOTIFY pgrst, 'reload schema'; 