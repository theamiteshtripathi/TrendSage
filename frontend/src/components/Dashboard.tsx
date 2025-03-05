import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'

interface Trend {
  id: string
  title: string
  description: string
  published_at: string
}

interface Blog {
  id: string
  title: string
  content: string
  created_at: string
}

export default function Dashboard() {
  const [trends, setTrends] = useState<Trend[]>([])
  const [blogs, setBlogs] = useState<Blog[]>([])
  const [topic, setTopic] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchTrends()
    fetchBlogs()
  }, [])

  const fetchTrends = async () => {
    try {
      const { data, error } = await supabase
        .from('news_articles')
        .select('*')
        .eq('analyzed', true)
        .order('published_at', { ascending: false })
      
      if (error) throw error
      setTrends(data || [])
    } catch (error) {
      console.error('Error fetching trends:', error)
    }
  }

  const fetchBlogs = async () => {
    try {
      const { data, error } = await supabase
        .from('blogs')
        .select('*')
        .order('created_at', { ascending: false })
      
      if (error) throw error
      setBlogs(data || [])
    } catch (error) {
      console.error('Error fetching blogs:', error)
    }
  }

  const analyzeTrends = async () => {
    if (!topic) return
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/analyze-trends', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic })
      })
      
      if (!response.ok) throw new Error('Failed to analyze trends')
      
      await fetchTrends()
      await fetchBlogs()
    } catch (error) {
      console.error('Error analyzing trends:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="dashboard">
      <div className="analyze-section">
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter topic to analyze"
        />
        <button onClick={analyzeTrends} disabled={loading}>
          {loading ? 'Analyzing...' : 'Analyze Trends'}
        </button>
      </div>

      <div className="content-grid">
        <div className="trends-section">
          <h2>Latest Trends</h2>
          <div className="trends-list">
            {trends.map((trend: Trend) => (
              <div key={trend.id} className="trend-card">
                <h3>{trend.title}</h3>
                <p>{trend.description}</p>
                <small>{new Date(trend.published_at).toLocaleDateString()}</small>
              </div>
            ))}
          </div>
        </div>

        <div className="blogs-section">
          <h2>Generated Blog Posts</h2>
          <div className="blogs-list">
            {blogs.map((blog: Blog) => (
              <div key={blog.id} className="blog-card">
                <h3>{blog.title}</h3>
                <div className="blog-content">{blog.content}</div>
                <small>{new Date(blog.created_at).toLocaleDateString()}</small>
              </div>
            ))}
          </div>
        </div>
      </div>

      <style jsx>{`
        .dashboard {
          padding: 20px;
          max-width: 1200px;
          margin: 0 auto;
        }

        .analyze-section {
          margin-bottom: 30px;
          display: flex;
          gap: 10px;
        }

        input {
          padding: 10px;
          border: 1px solid #ddd;
          border-radius: 4px;
          flex: 1;
        }

        button {
          padding: 10px 20px;
          background: #0070f3;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }

        button:disabled {
          background: #ccc;
        }

        .content-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
        }

        .trend-card, .blog-card {
          padding: 15px;
          border: 1px solid #eee;
          border-radius: 8px;
          margin-bottom: 15px;
        }

        .blog-content {
          max-height: 200px;
          overflow-y: auto;
          margin: 10px 0;
        }

        h2 {
          margin-bottom: 20px;
        }

        h3 {
          margin: 0 0 10px 0;
        }

        small {
          color: #666;
        }
      `}</style>
    </div>
  )
} 