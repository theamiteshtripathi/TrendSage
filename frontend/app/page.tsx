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

// Categories for navigation
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

  const handleChatWithTrends = (blogId?: string) => {
    const id = blogId || currentBlogPost?.id
    if (id) {
      router.push(`/chat/${id}`)
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center relative overflow-hidden">
        {/* Animated background elements */}
        <div className="absolute inset-0 z-0">
          <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-gradient-to-r from-[#1791c8]/20 to-transparent blur-3xl"></div>
          <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-gradient-to-r from-transparent to-[#1a73e8]/20 blur-3xl"></div>
          <div className="absolute top-[30%] right-[10%] w-[20%] h-[20%] rounded-full bg-[#1791c8]/10 blur-2xl"></div>
          <div className="absolute bottom-[30%] left-[10%] w-[20%] h-[20%] rounded-full bg-[#1a73e8]/10 blur-2xl"></div>
        </div>
        
        {/* Authentication component */}
        <div className="z-10">
          <AuthComponent />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <Header 
        categories={categories} 
        activeCategory={activeCategory} 
        onCategoryClick={handleCategoryClick} 
      />
      
      <main className="container mx-auto px-4 py-8">
        <HeroSection 
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          onSearch={() => analyzeTrends()}
          isLoading={isLoading}
        />
        
        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        
        {isAnalyzing && (
          <div className="mt-12">
            {!analysisComplete ? (
              <LoadingAnimation message={`Analyzing trends for "${searchQuery}"...`} />
            ) : (
              <div className="text-center mb-12">
                <SuccessAnimation title={searchQuery} />
                <div className="mt-6 flex justify-center space-x-4">
                  <Button 
                    onClick={() => handleReadAnalysis(currentBlogPost?.id || "")}
                    className="btn-futuristic"
                  >
                    <BookOpen className="mr-2 h-5 w-5" />
                    Read Analysis
                  </Button>
                  <Button 
                    onClick={() => handleChatWithTrends()}
                    variant="outline" 
                    className="border-primary/50 hover:bg-primary/20"
                  >
                    <MessageSquare className="mr-2 h-5 w-5" />
                    Chat with Trends
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
        
        {!isAnalyzing && blogPosts.length > 0 && (
          <>
            <div className="mt-16 mb-8 text-center">
              <h2 className="text-3xl font-bold gradient-text">Latest Trend Analysis</h2>
              <p className="text-muted-foreground mt-2">AI-generated insights on trending topics</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {blogPosts.map((post) => (
                <BlogPost
                  key={post.id}
                  title={post.title}
                  content={post.content}
                  category={post.category}
                  image_url={post.image_url}
                  onReadClick={() => handleReadAnalysis(post.id)}
                  onChatClick={() => handleChatWithTrends(post.id)}
                />
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  )
}

