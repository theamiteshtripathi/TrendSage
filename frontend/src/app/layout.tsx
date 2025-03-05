import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'News Tracker',
  description: 'Track and analyze news trends with AI',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <nav className="bg-gray-800 text-white p-4">
          <div className="container mx-auto">
            <div className="flex justify-between items-center">
              <h1 className="text-xl font-bold">News Tracker</h1>
              <div className="space-x-4">
                <a href="/" className="hover:text-gray-300">Home</a>
                <a href="/dashboard" className="hover:text-gray-300">Dashboard</a>
              </div>
            </div>
          </div>
        </nav>
        {children}
      </body>
    </html>
  )
} 