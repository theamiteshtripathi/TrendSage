"use client"

import React from 'react';
import { Button } from '@/components/ui/button';
import { MessageSquare, BookOpen } from 'lucide-react';

interface BlogPostProps {
  title: string;
  content: string;
  category: string;
  image_url?: string;
  onChatClick: () => void;
  onReadClick: () => void;
}

export function BlogPost({ title, content, category, image_url, onChatClick, onReadClick }: BlogPostProps) {
  // Safely truncate content to avoid rendering issues
  const truncatedContent = content && content.length > 200 
    ? content.slice(0, 200) + '...' 
    : content || '';

  // Extract first paragraph for description
  const description = truncatedContent.split('\n')[0];

  return (
    <div className="bg-card rounded-lg shadow-lg overflow-hidden transform transition-all duration-300 hover:translate-y-[-4px] hover:shadow-xl flex flex-col h-full">
      {/* Image Section */}
      <div className="aspect-video overflow-hidden bg-muted">
        {image_url ? (
          <img
            src={image_url}
            alt={title}
            className="h-full w-full object-cover transition-transform hover:scale-105"
          />
        ) : (
          <div className="h-full w-full bg-gradient-to-br from-blue-900 to-indigo-900 flex items-center justify-center">
            <span className="text-2xl font-bold text-white">{title.charAt(0)}</span>
          </div>
        )}
      </div>
      
      {/* Content Section */}
      <div className="p-4 flex-1 flex flex-col">
        <div className="mb-2">
          <span className="inline-block px-3 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 mb-2">
            {category}
          </span>
          <h2 className="text-xl font-bold line-clamp-2">{title}</h2>
        </div>
        
        <p className="text-muted-foreground text-sm mb-4 line-clamp-3">
          {description}
        </p>
        
        <div className="mt-auto flex space-x-2">
          <Button 
            onClick={onReadClick}
            className="flex-1 flex items-center justify-center space-x-1"
            size="sm"
          >
            <BookOpen className="h-4 w-4" />
            <span>Read</span>
          </Button>
          
          <Button 
            onClick={onChatClick}
            variant="outline"
            className="flex-1 flex items-center justify-center space-x-1"
            size="sm"
          >
            <MessageSquare className="h-4 w-4" />
            <span>Chat</span>
          </Button>
        </div>
      </div>
    </div>
  );
}

export function BlogPostFull({ title, content, category, image_url }: Omit<BlogPostProps, 'onChatClick' | 'onReadClick'> & { image_url?: string }) {
  // Safely handle content
  const safeContent = content || '';

  return (
    <div className="bg-card rounded-lg shadow-lg overflow-hidden">
      {/* Hero Image */}
      {image_url && (
        <div className="w-full h-64 md:h-96 overflow-hidden">
          <img
            src={image_url}
            alt={title}
            className="w-full h-full object-cover"
          />
        </div>
      )}
      
      <div className="p-6 md:p-8">
        <div className="mb-6">
          <span className="inline-block px-3 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 mb-2">
            {category}
          </span>
          <h1 className="text-3xl md:text-4xl font-bold">{title}</h1>
        </div>
        
        <div className="prose dark:prose-invert max-w-none">
          <div dangerouslySetInnerHTML={{ __html: safeContent.replace(/\n/g, '<br/>') }} />
        </div>
      </div>
    </div>
  );
} 