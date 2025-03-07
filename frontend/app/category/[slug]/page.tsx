"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Loader2 } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Header } from "@/components/header"
import { BlogPost } from "@/components/blog-post"
import { apiClient } from "@/lib/api"

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

export default function CategoryPage() {
  const router = useRouter()
  const params = useParams()
  const [blogPosts, setBlogPosts] = useState<BlogPostType[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")
  const [activeCategory, setActiveCategory] = useState("All")

  useEffect(() => {
    const fetchCategoryPosts = async () => {
      if (!params.slug) return

      try {
        setIsLoading(true)
        const category = decodeURIComponent(params.slug as string)
        setActiveCategory(category)
        
        const response = await apiClient.getBlogs(category)
        if (response && response.length > 0) {
          setBlogPosts(response)
        } else {
          setBlogPosts([])
        }
      } catch (err) {
        console.error("Error fetching category posts:", err)
        setError("Failed to load blog posts for this category")
      } finally {
        setIsLoading(false)
      }
    }

    fetchCategoryPosts()
  }, [params.slug])

  const handleCategoryClick = (category: string) => {
    if (category === "All") {
      router.push("/")
    } else {
      router.push(`/category/${encodeURIComponent(category)}`)
    }
  }

  const handleReadAnalysis = (postId: string) => {
    router.push(`/blog/${postId}`)
  }

  const handleChatWithTrends = () => {
    // This will be implemented later
    alert("Chat with Trends feature coming soon!")
  }

  return (
    <div className="min-h-screen bg-background">
      <Header 
        categories={categories} 
        activeCategory={activeCategory} 
        onCategoryClick={handleCategoryClick} 
      />

      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold">{activeCategory} Trends</h1>
          <p className="text-muted-foreground mt-2">
            Discover the latest trends in {activeCategory.toLowerCase()}
          </p>
        </div>

        {isLoading && (
          <div className="flex justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        )}

        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {!isLoading && blogPosts.length === 0 && !error && (
          <div className="text-center py-12">
            <h2 className="text-2xl font-semibold mb-2">No blog posts found</h2>
            <p className="text-muted-foreground">
              There are no blog posts in the {activeCategory} category yet.
            </p>
          </div>
        )}

        {blogPosts.length > 0 && (
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-1">
            {blogPosts.map((post) => (
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
        )}
      </main>
    </div>
  )
} 