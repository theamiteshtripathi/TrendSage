-- Enable Row Level Security
ALTER TABLE auth.users ENABLE ROW LEVEL SECURITY;

-- Create news_articles table
CREATE TABLE IF NOT EXISTS public.news_articles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    source TEXT NOT NULL,
    author TEXT,
    title TEXT NOT NULL,
    description TEXT,
    url TEXT UNIQUE NOT NULL,
    url_to_image TEXT,
    published_at TIMESTAMP WITH TIME ZONE NOT NULL,
    content TEXT,
    category TEXT DEFAULT 'Miscellaneous',
    trend_score FLOAT DEFAULT 1.0,
    analyzed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
    user_id UUID REFERENCES auth.users(id)
);

-- Create blogs table
CREATE TABLE IF NOT EXISTS public.blogs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT DEFAULT 'Miscellaneous',
    trend_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
    user_id UUID REFERENCES auth.users(id)
);

-- Create user_preferences table
CREATE TABLE IF NOT EXISTS public.user_preferences (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) UNIQUE NOT NULL,
    topics TEXT[] DEFAULT '{}',
    notification_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

-- Create workflow_cache table
CREATE TABLE IF NOT EXISTS public.workflow_cache (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    topic TEXT NOT NULL,
    category TEXT NOT NULL,
    result JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

-- Enable Row Level Security on all tables
ALTER TABLE public.news_articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.blogs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflow_cache ENABLE ROW LEVEL SECURITY;

-- Create policies for news_articles
CREATE POLICY "Enable read access for all users" ON public.news_articles
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for service role" ON public.news_articles
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update for service role" ON public.news_articles
    FOR UPDATE USING (true);

-- Create policies for blogs
CREATE POLICY "Public read access for blogs" ON public.blogs
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for service role" ON public.blogs
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update for service role" ON public.blogs
    FOR UPDATE USING (true);

-- Create policies for user_preferences
CREATE POLICY "Enable read for users" ON public.user_preferences
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Enable insert for authenticated users" ON public.user_preferences
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Enable update for users" ON public.user_preferences
    FOR UPDATE USING (auth.uid() = user_id);

-- Create policies for workflow_cache
CREATE POLICY "Public read access for workflow_cache" ON public.workflow_cache
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for service role" ON public.workflow_cache
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update for service role" ON public.workflow_cache
    FOR UPDATE USING (true);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_news_articles_analyzed ON public.news_articles(analyzed);
CREATE INDEX IF NOT EXISTS idx_news_articles_published_at ON public.news_articles(published_at);
CREATE INDEX IF NOT EXISTS idx_blogs_created_at ON public.blogs(created_at);
CREATE INDEX IF NOT EXISTS idx_news_articles_category ON public.news_articles(category);
CREATE INDEX IF NOT EXISTS idx_blogs_category ON public.blogs(category);
CREATE INDEX IF NOT EXISTS idx_news_articles_trend_score ON public.news_articles(trend_score);
CREATE INDEX IF NOT EXISTS idx_blogs_trend_score ON public.blogs(trend_score);
CREATE INDEX IF NOT EXISTS idx_workflow_cache_topic ON public.workflow_cache(topic);
CREATE INDEX IF NOT EXISTS idx_workflow_cache_category ON public.workflow_cache(category);
CREATE INDEX IF NOT EXISTS idx_workflow_cache_created_at ON public.workflow_cache(created_at);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON public.blogs
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON public.user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON public.workflow_cache
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- Refresh the schema cache
NOTIFY pgrst, 'reload schema'; 

