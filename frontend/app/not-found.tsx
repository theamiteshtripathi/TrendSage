import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background">
      <div className="container flex max-w-md flex-col items-center justify-center space-y-6 text-center">
        <div className="animate-fade-in">
          <svg 
            viewBox="0 0 24 24" 
            className="h-24 w-24 text-blue-600"
            fill="none"
            stroke="currentColor"
            strokeWidth="1"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="12" cy="12" r="10" />
            <path d="M16 16s-1.5-2-4-2-4 2-4 2" />
            <line x1="9" y1="9" x2="9.01" y2="9" />
            <line x1="15" y1="9" x2="15.01" y2="9" />
          </svg>
        </div>
        
        <h1 className="text-4xl font-bold tracking-tight animate-fade-in-delay-1">
          404 - Page Not Found
        </h1>
        
        <p className="text-muted-foreground animate-fade-in-delay-2">
          The page you're looking for doesn't exist or has been moved.
        </p>
        
        <div className="animate-fade-in-delay-3">
          <Button asChild>
            <Link href="/">
              Return to Home
            </Link>
          </Button>
        </div>
      </div>
    </div>
  )
} 