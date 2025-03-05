-- Add missing columns to news_articles
ALTER TABLE public.news_articles 
ADD COLUMN IF NOT EXISTS category TEXT DEFAULT 'Miscellaneous',
ADD COLUMN IF NOT EXISTS trend_score FLOAT DEFAULT 1.0;

-- Add missing columns to blogs
ALTER TABLE public.blogs 
ADD COLUMN IF NOT EXISTS category TEXT DEFAULT 'Miscellaneous',
ADD COLUMN IF NOT EXISTS trend_score FLOAT DEFAULT 1.0;

-- Create indexes for new columns
CREATE INDEX IF NOT EXISTS idx_news_articles_category ON public.news_articles(category);
CREATE INDEX IF NOT EXISTS idx_blogs_category ON public.blogs(category);
CREATE INDEX IF NOT EXISTS idx_news_articles_trend_score ON public.news_articles(trend_score);
CREATE INDEX IF NOT EXISTS idx_blogs_trend_score ON public.blogs(trend_score);

-- Refresh the schema cache
NOTIFY pgrst, 'reload schema'; 