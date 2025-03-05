"use client"

import { useState, useEffect } from "react"
import axios from "axios"
import { Search, Loader2, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import Image from "next/image"
import AuthComponent from "@/components/auth"
import { supabase } from "@/lib/supabase"

// Types
interface Headline {
  title: string
  description: string
  url: string
  image?: string
}

// Sample categories for the navigation bar
const categories = ["All", "Tech", "Culture", "Business", "Fashion", "Sports", "Politics", "Health"]

export default function NewsTracker() {
  const [searchQuery, setSearchQuery] = useState("")
  const [headlines, setHeadlines] = useState<Headline[]>([])
  const [blogPost, setBlogPost] = useState("")
  const [blogPostUrl, setBlogPostUrl] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [activeCategory, setActiveCategory] = useState("All")
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    const { data: authListener } = supabase.auth.onAuthStateChange((event, session) => {
      setIsAuthenticated(!!session)
    })

    return () => {
      authListener?.subscription.unsubscribe()
    }
  }, [])

  const fetchNews = async (topic = searchQuery) => {
    if (!topic.trim()) {
      setError("Please enter a search topic")
      return
    }

    setIsLoading(true)
    setError("")
    setHeadlines([])
    setBlogPost("")
    setBlogPostUrl("")

    try {
      const response = await axios.post("https://example.com/fetchNews", {
        topic: topic,
        count: 10,
      })

      if (response.data && response.data.headlines) {
        setHeadlines(response.data.headlines)
      }

      if (response.data && response.data.blogPost) {
        if (typeof response.data.blogPost === "string") {
          setBlogPost(response.data.blogPost)
        } else if (response.data.blogPost.url) {
          setBlogPostUrl(response.data.blogPost.url)
        }
      }
    } catch (err) {
      setError("Failed to fetch news. Please try again.")
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      fetchNews()
    }
  }

  const handleCategoryClick = (category: string) => {
    setActiveCategory(category)
    if (category !== "All") {
      fetchNews(category)
    }
  }

  const truncateText = (text: string, maxLength = 100) => {
    return text.length > maxLength ? text.slice(0, maxLength) + "..." : text
  }

  const getPlaceholderImage = (index: number) => {
    return `/placeholder-${(index % 3) + 1}.jpg`
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
      {/* Navigation Bar */}
      <nav className="border-b border-border">
        <div className="container mx-auto px-4 py-4">
          <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-foreground">News Tracker</h1>
            </div>
            <div className="flex items-center space-x-4">
              {categories.map((category) => (
                <Button
                  key={category}
                  variant={activeCategory === category ? "default" : "ghost"}
                  onClick={() => handleCategoryClick(category)}
                  className="px-3 py-2 text-sm"
                >
                  {category}
                </Button>
              ))}
            </div>
          </div>
        </div>
      </nav>

      {/* Search Section */}
      <section className="container mx-auto px-4 py-8">
        <div className="flex flex-col space-y-4 md:flex-row md:items-center md:space-x-4 md:space-y-0">
          <div className="relative flex-1">
            <Input
              type="text"
              placeholder="Enter a topic..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              className="w-full pl-10 pr-4"
            />
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 transform text-muted-foreground" />
          </div>
          <Button
            onClick={() => fetchNews()}
            disabled={isLoading}
            className="w-full md:w-auto"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Searching...
              </>
            ) : (
              "Search"
            )}
          </Button>
        </div>
      </section>

      <main>
        {/* Hero Section */}
        <section className="bg-gradient-to-r from-gray-800 to-gray-900 py-16 md:py-24">
          <div className="container mx-auto px-4 text-center">
            <h2 className="mb-6 text-4xl font-extrabold tracking-tight md:text-5xl lg:text-6xl">
              Discover the Latest Trends with News Tracker
            </h2>
            <p className="mx-auto mb-8 max-w-2xl text-lg text-gray-300">
              Fetch the top headlines and generated blog posts on any topic.
            </p>
            <div className="mx-auto mb-8 flex max-w-md flex-col space-y-4 sm:flex-row sm:space-x-4 sm:space-y-0">
              <Input
                type="text"
                placeholder="Enter a topic..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={isLoading}
                className="bg-gray-700 text-white placeholder:text-gray-400"
              />
              <Button
                onClick={() => fetchNews()}
                disabled={isLoading}
                className="bg-blue-600 text-white hover:bg-blue-700"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Loading
                  </>
                ) : (
                  <>
                    <Search className="mr-2 h-4 w-4" />
                    Search
                  </>
                )}
              </Button>
            </div>
          </div>
        </section>

        {/* Error Alert */}
        {error && (
          <div className="container mx-auto px-4 py-6">
            <Alert variant="destructive" className="bg-red-900 text-white">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          </div>
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="container mx-auto flex justify-center px-4 py-12">
            <div className="flex flex-col items-center">
              <Loader2 className="h-12 w-12 animate-spin text-blue-400" />
              <p className="mt-4 text-gray-300">Fetching the latest news...</p>
            </div>
          </div>
        )}

        {/* Headlines Section */}
        {headlines.length > 0 && (
          <section className="container mx-auto px-4 py-12">
            <div className="mb-8 flex items-center justify-between">
              <h3 className="text-2xl font-bold text-white">Top Headlines</h3>
              <span className="text-sm text-gray-400">Showing {headlines.length} results</span>
            </div>

            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {headlines.map((headline, index) => (
                <Card
                  key={index}
                  className="overflow-hidden bg-gray-800 transition-all duration-300 hover:scale-[1.02] hover:shadow-lg"
                >
                  <div className="aspect-video overflow-hidden bg-gray-700">
                    <Image
                      src={headline.image || getPlaceholderImage(index)}
                      alt={headline.title || "News headline"}
                      width={400}
                      height={200}
                      className="h-full w-full object-cover transition-transform duration-500 hover:scale-110"
                    />
                  </div>
                  <CardContent className="p-4">
                    <h4 className="mb-2 line-clamp-2 text-lg font-semibold text-white">
                      {headline.title || `Headline ${index + 1}`}
                    </h4>
                    <p className="line-clamp-3 text-sm text-gray-300">
                      {headline.description ||
                        truncateText(headline.title || `Description for headline ${index + 1}`, 120)}
                    </p>
                  </CardContent>
                  <CardFooter className="border-t border-gray-700 p-4">
                    <a
                      href={headline.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center text-sm font-medium text-blue-400 hover:text-blue-300"
                    >
                      Read full article
                      <ChevronRight className="ml-1 h-4 w-4" />
                    </a>
                  </CardFooter>
                </Card>
              ))}
            </div>
          </section>
        )}

        {/* Blog Post Section */}
        {(blogPost || blogPostUrl) && (
          <section className="container mx-auto px-4 py-12">
            <h3 className="mb-6 text-2xl font-bold text-white">Generated Blog Post</h3>
            <Card className="bg-gray-800 p-6">
              {blogPostUrl ? (
                <div className="rounded-lg bg-gray-700 p-8 text-center">
                  <h4 className="mb-4 text-xl font-semibold text-white">Your blog post is ready!</h4>
                  <a
                    href={blogPostUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center rounded-md bg-blue-600 px-6 py-3 text-white transition-colors hover:bg-blue-700"
                  >
                    View Generated Blog Post
                    <ChevronRight className="ml-2 h-4 w-4" />
                  </a>
                </div>
              ) : (
                <div className="prose prose-invert max-w-none">
                  {blogPost.split("\n").map((paragraph, index) =>
                    paragraph.trim() ? (
                      <p key={index} className="mb-4 text-gray-300">
                        {paragraph}
                      </p>
                    ) : null,
                  )}
                </div>
              )}
            </Card>
          </section>
        )}

        {/* Empty State */}
        {!isLoading && headlines.length === 0 && !error && (
          <section className="container mx-auto px-4 py-16 text-center">
            <div className="mx-auto max-w-md">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="mx-auto h-16 w-16 text-gray-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1}
                  d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"
                />
              </svg>
              <h3 className="mt-4 text-xl font-semibold text-white">No headlines to display</h3>
              <p className="mt-2 text-gray-400">
                Enter a topic in the search bar above or select a category to fetch the latest news.
              </p>
            </div>
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 py-8">
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm text-gray-400">© {new Date().getFullYear()} News Tracker. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}

