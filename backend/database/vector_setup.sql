-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the blog_embeddings table
CREATE TABLE IF NOT EXISTS public.blog_embeddings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    blog_id UUID REFERENCES public.blogs(id) ON DELETE CASCADE,
    content TEXT,
    title TEXT,
    embedding vector(1536),  -- OpenAI embeddings are 1536 dimensions
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

-- Create an index for faster similarity search
CREATE INDEX IF NOT EXISTS blog_embeddings_embedding_idx ON public.blog_embeddings USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

-- Enable RLS on the blog_embeddings table
ALTER TABLE public.blog_embeddings ENABLE ROW LEVEL SECURITY;

-- Create policies for blog_embeddings
CREATE POLICY "Public read access for blog_embeddings" ON public.blog_embeddings
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for service role" ON public.blog_embeddings
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update for service role" ON public.blog_embeddings
    FOR UPDATE USING (true);

-- Create a function for similarity search
CREATE OR REPLACE FUNCTION match_blog_embeddings(
    query_embedding vector(1536),
    match_threshold float,
    match_count int
)
RETURNS TABLE (
    id UUID,
    blog_id UUID,
    content TEXT,
    title TEXT,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        be.id,
        be.blog_id,
        be.content,
        be.title,
        1 - (be.embedding <=> query_embedding) as similarity
    FROM
        public.blog_embeddings be
    WHERE
        1 - (be.embedding <=> query_embedding) > match_threshold
    ORDER BY
        similarity DESC
    LIMIT match_count;
END;
$$;

-- Grant permissions
GRANT ALL ON public.blog_embeddings TO service_role;
GRANT ALL ON public.blog_embeddings TO anon;
GRANT ALL ON public.blog_embeddings TO authenticated;
GRANT EXECUTE ON FUNCTION match_blog_embeddings TO service_role;
GRANT EXECUTE ON FUNCTION match_blog_embeddings TO anon;
GRANT EXECUTE ON FUNCTION match_blog_embeddings TO authenticated;

-- Refresh the schema cache
NOTIFY pgrst, 'reload schema'; 