"use client"

import React from 'react';
import { Button } from '@/components/ui/button';
import { MessageSquare, BookOpen } from 'lucide-react';

interface BlogPostProps {
  title: string;
  content: string;
  category: string;
  onChatClick: () => void;
  onReadClick: () => void;
}

export function BlogPost({ title, content, category, onChatClick, onReadClick }: BlogPostProps) {
  // Safely truncate content to avoid rendering issues
  const truncatedContent = content && content.length > 500 
    ? content.slice(0, 500) + '...' 
    : content || '';

  return (
    <div className="bg-card rounded-lg shadow-lg overflow-hidden transform transition-all duration-300 hover:translate-y-[-4px] hover:shadow-xl">
      <div className="p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <span className="inline-block px-3 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 mb-2">
              {category}
            </span>
            <h2 className="text-2xl font-bold">{title}</h2>
          </div>
        </div>
        
        <div className="prose dark:prose-invert max-w-none mb-6">
          <div dangerouslySetInnerHTML={{ __html: truncatedContent.replace(/\n/g, '<br/>') }} />
        </div>
        
        <div className="flex space-x-4">
          <Button 
            onClick={onReadClick}
            className="flex items-center space-x-2"
          >
            <BookOpen className="h-4 w-4" />
            <span>Read Analysis</span>
          </Button>
          
          <Button 
            onClick={onChatClick}
            variant="outline"
            className="flex items-center space-x-2"
          >
            <MessageSquare className="h-4 w-4" />
            <span>Chat with Trends</span>
          </Button>
        </div>
      </div>
    </div>
  );
}

export function BlogPostFull({ title, content, category }: Omit<BlogPostProps, 'onChatClick' | 'onReadClick'>) {
  // Safely handle content
  const safeContent = content || '';

  return (
    <div className="bg-card rounded-lg shadow-lg overflow-hidden">
      <div className="p-6">
        <div className="mb-6">
          <span className="inline-block px-3 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 mb-2">
            {category}
          </span>
          <h1 className="text-3xl font-bold">{title}</h1>
        </div>
        
        <div className="prose dark:prose-invert max-w-none">
          <div dangerouslySetInnerHTML={{ __html: safeContent.replace(/\n/g, '<br/>') }} />
        </div>
      </div>
    </div>
  );
} 