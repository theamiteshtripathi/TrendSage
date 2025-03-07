"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { ArrowLeft, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { BlogPostFull } from "@/components/blog-post"
import { Header } from "@/components/header"
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

export default function BlogPostPage() {
  const router = useRouter()
  const params = useParams()
  const [blogPost, setBlogPost] = useState<BlogPostType | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")
  const [activeCategory, setActiveCategory] = useState("All")

  useEffect(() => {
    const fetchBlogPost = async () => {
      if (!params.id) return

      try {
        setIsLoading(true)
        // This is a placeholder - you'll need to implement a getPost endpoint
        const response = await apiClient.getBlogs()
        const post = response.find((p: BlogPostType) => p.id === params.id)
        
        if (post) {
          setBlogPost(post)
          setActiveCategory(post.category || "Miscellaneous")
        } else {
          setError("Blog post not found")
        }
      } catch (err) {
        console.error("Error fetching blog post:", err)
        setError("Failed to load blog post")
      } finally {
        setIsLoading(false)
      }
    }

    fetchBlogPost()
  }, [params.id])

  const handleCategoryClick = (category: string) => {
    setActiveCategory(category)
    router.push("/")
  }

  return (
    <div className="min-h-screen bg-background">
      <Header 
        categories={categories} 
        activeCategory={activeCategory} 
        onCategoryClick={handleCategoryClick} 
      />

      <main className="container mx-auto px-4 py-8">
        <Button
          variant="ghost"
          className="mb-6"
          onClick={() => router.back()}
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>

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

        {blogPost && (
          <BlogPostFull
            title={blogPost.title || "Untitled Post"}
            content={blogPost.content || "No content available"}
            category={blogPost.category || "Miscellaneous"}
          />
        )}
      </main>
    </div>
  )
} 