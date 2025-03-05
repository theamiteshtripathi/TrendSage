-- Add missing columns to news_articles
ALTER TABLE public.news_articles 
ADD COLUMN IF NOT EXISTS category TEXT DEFAULT 'Miscellaneous',
ADD COLUMN IF NOT EXISTS trend_score FLOAT DEFAULT 1.0,
ADD COLUMN IF NOT EXISTS image_url TEXT,
ADD COLUMN IF NOT EXISTS analyzed BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS source TEXT,
ADD COLUMN IF NOT EXISTS author TEXT,
ADD COLUMN IF NOT EXISTS published_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
ADD COLUMN IF NOT EXISTS url_to_image TEXT;

-- Add missing columns to blogs
ALTER TABLE public.blogs 
ADD COLUMN IF NOT EXISTS category TEXT DEFAULT 'Miscellaneous',
ADD COLUMN IF NOT EXISTS trend_score FLOAT DEFAULT 1.0,
ADD COLUMN IF NOT EXISTS image_url TEXT,
ADD COLUMN IF NOT EXISTS source_articles JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS author TEXT,
ADD COLUMN IF NOT EXISTS published_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'draft',
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_news_articles_category ON public.news_articles(category);
CREATE INDEX IF NOT EXISTS idx_blogs_category ON public.blogs(category);
CREATE INDEX IF NOT EXISTS idx_news_articles_trend_score ON public.news_articles(trend_score);
CREATE INDEX IF NOT EXISTS idx_blogs_trend_score ON public.blogs(trend_score);
CREATE INDEX IF NOT EXISTS idx_news_articles_analyzed ON public.news_articles(analyzed);
CREATE INDEX IF NOT EXISTS idx_news_articles_published_at ON public.news_articles(published_at);
CREATE INDEX IF NOT EXISTS idx_blogs_published_at ON public.blogs(published_at);
CREATE INDEX IF NOT EXISTS idx_blogs_status ON public.blogs(status);

-- Add constraints
ALTER TABLE public.news_articles
ALTER COLUMN url SET NOT NULL,
ADD CONSTRAINT news_articles_url_unique UNIQUE (url);

ALTER TABLE public.blogs
ALTER COLUMN title SET NOT NULL,
ALTER COLUMN content SET NOT NULL;

-- Create updated_at trigger for both tables if not exists
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS set_news_articles_updated_at ON public.news_articles;
CREATE TRIGGER set_news_articles_updated_at
    BEFORE UPDATE ON public.news_articles
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

DROP TRIGGER IF EXISTS set_blogs_updated_at ON public.blogs;
CREATE TRIGGER set_blogs_updated_at
    BEFORE UPDATE ON public.blogs
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- Refresh the schema cache
NOTIFY pgrst, 'reload schema'; 