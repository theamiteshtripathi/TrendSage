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
import { Button } from "@/components/ui/button"
import { BookOpen, MessageSquare } from "lucide-react"

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
  const [currentPage, setCurrentPage] = useState(1)
  const postsPerPage = 9 // Show 9 posts per page (3x3 grid)

  useEffect(() => {
    const { data: authListener } = supabase.auth.onAuthStateChange((event, session) => {
      setIsAuthenticated(!!session)
    })

    // Fetch initial blog posts
    fetchBlogPosts()

    // Set up a refresh interval (every 30 seconds)
    const refreshInterval = setInterval(() => {
      fetchBlogPosts(activeCategory !== "All" ? activeCategory : undefined);
    }, 30000);

    return () => {
      authListener?.subscription.unsubscribe()
      clearInterval(refreshInterval)
    }
  }, [activeCategory])

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
          // Fetch all blog posts to ensure we have the latest data
          const blogsResponse = await apiClient.getBlogs()
          if (blogsResponse && blogsResponse.length > 0) {
            // Check if there's a blog post with a title containing our search query
            const relevantBlog = blogsResponse.find((blog: BlogPostType) => 
              blog.title.toLowerCase().includes(topic.toLowerCase())
            )
            
            // Always update the blog posts list with the latest data
            setBlogPosts(blogsResponse)
            
            if (relevantBlog) {
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
          // Even if we don't find a blog with the exact topic, still show the latest blogs
          try {
            const latestBlogs = await apiClient.getBlogs()
            if (latestBlogs && latestBlogs.length > 0) {
              setBlogPosts(latestBlogs)
              setCurrentBlogPost(latestBlogs[0])
              setAnalysisComplete(true)
            }
          } catch (error) {
            console.error("Error fetching latest blogs:", error)
          }
          setError("Analysis is taking longer than expected. Showing the latest blog posts instead.")
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
      // Refresh blog posts one more time after analysis is complete
      fetchBlogPosts(activeCategory !== "All" ? activeCategory : undefined)
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
    if (currentBlogPost) {
      router.push(`/chat/${currentBlogPost.id}`);
    } else if (blogPosts.length > 0) {
      router.push(`/chat/${blogPosts[0].id}`);
    } else {
      setError("No blog posts available to chat with. Please try analyzing a topic first.");
    }
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
            <div className="flex justify-center mt-6 space-x-4">
              <Button 
                onClick={() => handleReadAnalysis(currentBlogPost.id)}
                className="flex items-center justify-center space-x-1"
              >
                <BookOpen className="h-4 w-4 mr-2" />
                <span>Read Analysis</span>
              </Button>
              
              <Button 
                onClick={() => router.push(`/chat/${currentBlogPost.id}`)}
                variant="outline"
                className="flex items-center justify-center space-x-1"
              >
                <MessageSquare className="h-4 w-4 mr-2" />
                <span>Chat with Trends</span>
              </Button>
            </div>
          </div>
        )}

        {/* Blog Posts Section */}
        {blogPosts.length > 0 && (
          <section className="py-12">
            <div className="mb-8 text-center">
              <h2 className="text-3xl font-bold gradient-text">Latest Trend Analysis</h2>
              <p className="text-muted-foreground mt-2">AI-generated insights on trending topics</p>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {blogPosts.map((post) => (
                <BlogPost
                  key={post.id}
                  title={post.title || "Untitled Post"}
                  content={post.content || "No content available"}
                  category={post.category || "Miscellaneous"}
                  onChatClick={() => router.push(`/chat/${post.id}`)}
                  onReadClick={() => handleReadAnalysis(post.id)}
                />
              ))}
            </div>
            
            {/* Add pagination if needed in the future */}
            {blogPosts.length > postsPerPage && (
              <div className="flex justify-center mt-8">
                <Button 
                  variant="outline" 
                  onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                  disabled={currentPage === 1}
                  className="mr-2"
                >
                  Previous
                </Button>
                <span className="flex items-center mx-4">
                  Page {currentPage} of {Math.ceil(blogPosts.length / postsPerPage)}
                </span>
                <Button 
                  variant="outline" 
                  onClick={() => setCurrentPage(prev => Math.min(prev + 1, Math.ceil(blogPosts.length / postsPerPage)))}
                  disabled={currentPage === Math.ceil(blogPosts.length / postsPerPage)}
                  className="ml-2"
                >
                  Next
                </Button>
              </div>
            )}
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

