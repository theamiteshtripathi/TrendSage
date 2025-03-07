"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Alert, AlertDescription } from "@/components/ui/alert"
import AuthComponent from "@/components/auth"
import { supabase } from "@/lib/supabase"
import { apiClient } from "@/lib/api"
import { Header } from "@/components/header"
import { HeroSection } from "@/components/hero-section"
import { LoadingAnimation, SuccessAnimation } from "@/components/ui/loading-animation"
import { BlogPost } from "@/components/blog-post"

// Types
interface Headline {
  title: string
  description: string
  url: string
  image?: string
}

interface NewsArticle {
  title: string
  description: string
  url: string
  image_url?: string
  category: string
  analyzed: boolean
}

interface BlogPostType {
  id: string
  title: string
  content: string
  category: string
  created_at: string
  image_url?: string
}

// Sample categories for the navigation bar
const categories = ["All", "Tech", "Business", "Health", "Science", "Sports", "Entertainment", "Politics", "Miscellaneous"]

export default function TrendSage() {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState("")
  const [headlines, setHeadlines] = useState<Headline[]>([])
  const [blogPosts, setBlogPosts] = useState<BlogPostType[]>([])
  const [currentBlogPost, setCurrentBlogPost] = useState<BlogPostType | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisComplete, setAnalysisComplete] = useState(false)
  const [error, setError] = useState("")
  const [activeCategory, setActiveCategory] = useState("All")
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    const { data: authListener } = supabase.auth.onAuthStateChange((event, session) => {
      setIsAuthenticated(!!session)
    })

    // Fetch initial blog posts
    fetchBlogPosts()

    return () => {
      authListener?.subscription.unsubscribe()
    }
  }, [])

  const fetchBlogPosts = async (category?: string) => {
    try {
      const categoryParam = category && category !== "All" ? category : undefined
      const blogsResponse = await apiClient.getBlogs(categoryParam)
      if (blogsResponse && blogsResponse.length > 0) {
        setBlogPosts(blogsResponse)
        setCurrentBlogPost(blogsResponse[0])
      }
    } catch (err) {
      console.error("Error fetching blog posts:", err)
    }
  }

  const analyzeTrends = async (topic = searchQuery) => {
    if (!topic.trim()) {
      setError("Please enter a search topic")
      return
    }

    setIsLoading(true)
    setIsAnalyzing(true)
    setAnalysisComplete(false)
    setError("")

    try {
      // First analyze trends
      await apiClient.analyzeTrends(topic, activeCategory !== "All" ? activeCategory : undefined)
      
      // Poll for new blog posts every 3 seconds
      let attempts = 0
      const maxAttempts = 10
      const pollInterval = setInterval(async () => {
        attempts++
        try {
          const blogsResponse = await apiClient.getBlogs()
          if (blogsResponse && blogsResponse.length > 0) {
            // Check if there's a blog post with a title containing our search query
            const relevantBlog = blogsResponse.find((blog: BlogPostType) => 
              blog.title.toLowerCase().includes(topic.toLowerCase())
            )
            
            if (relevantBlog) {
              setBlogPosts(blogsResponse)
              setCurrentBlogPost(relevantBlog)
              setAnalysisComplete(true)
              clearInterval(pollInterval)
            }
          }
        } catch (pollError) {
          console.error("Error polling for blog posts:", pollError)
        }
        
        if (attempts >= maxAttempts) {
          clearInterval(pollInterval)
          setError("Analysis is taking longer than expected. Please check back later.")
        }
      }, 3000)
      
      // Fetch news articles
      const trendsResponse = await apiClient.getTrends(activeCategory !== "All" ? activeCategory : undefined)
      if (trendsResponse) {
        setHeadlines(trendsResponse.map((article: NewsArticle) => ({
          title: article.title,
          description: article.description,
          url: article.url,
          image: article.image_url
        })))
      }
    } catch (err) {
      setError("Failed to analyze trends. Please try again.")
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCategoryClick = (category: string) => {
    setActiveCategory(category)
    if (category === "All") {
      router.push("/")
    } else {
      router.push(`/category/${encodeURIComponent(category)}`)
    }
    fetchBlogPosts(category !== "All" ? category : undefined)
  }

  const handleReadAnalysis = (id: string) => {
    router.push(`/blog/${id}`);
  }

  const handleChatWithTrends = () => {
    // This will be implemented later
    alert("Chat with Trends feature coming soon!")
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <AuthComponent />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <Header 
        categories={categories} 
        activeCategory={activeCategory} 
        onCategoryClick={handleCategoryClick} 
      />

      {/* Hero Section */}
      <HeroSection
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        onSearch={() => analyzeTrends()}
        isLoading={isLoading}
      />

      <main className="container mx-auto px-4 py-8">
        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Loading Animation */}
        {isAnalyzing && !analysisComplete && (
          <div className="my-12">
            <LoadingAnimation message={`Analyzing trends for "${searchQuery}"...`} />
          </div>
        )}

        {/* Success Animation */}
        {analysisComplete && currentBlogPost && (
          <div className="my-12">
            <SuccessAnimation title={searchQuery} />
          </div>
        )}

        {/* Blog Posts Section */}
        {blogPosts.length > 0 && (
          <section className="py-12">
            <div className="mb-8">
              <h2 className="text-3xl font-bold">Latest Trend Analysis</h2>
              <p className="text-muted-foreground">AI-generated insights on trending topics</p>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {blogPosts.slice(0, 6).map((post) => (
                <BlogPost
                  key={post.id}
                  title={post.title || "Untitled Post"}
                  content={post.content || "No content available"}
                  category={post.category || "Miscellaneous"}
                  onChatClick={handleChatWithTrends}
                  onReadClick={() => handleReadAnalysis(post.id)}
                />
              ))}
            </div>
          </section>
        )}

        {/* Headlines Section */}
        {headlines.length > 0 && (
          <section className="py-12">
            <div className="mb-8">
              <h2 className="text-3xl font-bold">Related News</h2>
              <p className="text-muted-foreground">Latest headlines on this topic</p>
            </div>

            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {headlines.map((headline, index) => (
                <a
                  key={index}
                  href={headline.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group block overflow-hidden rounded-lg border bg-card transition-all hover:shadow-md"
                >
                  <div className="aspect-video overflow-hidden bg-muted">
                    {headline.image ? (
                      <img
                        src={headline.image}
                        alt={headline.title || "News headline"}
                        className="h-full w-full object-cover transition-transform group-hover:scale-105"
                      />
                    ) : (
                      <div className="flex h-full w-full items-center justify-center bg-muted">
                        <span className="text-muted-foreground">No image</span>
                      </div>
                    )}
                  </div>
                  <div className="p-4">
                    <h3 className="font-semibold line-clamp-2">{headline.title || "Untitled"}</h3>
                    <p className="mt-2 text-sm text-muted-foreground line-clamp-3">
                      {headline.description || "No description available"}
                    </p>
                  </div>
                </a>
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  )
}

