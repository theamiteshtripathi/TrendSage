"use client"

import React from 'react';
import { Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

interface HeroSectionProps {
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  onSearch: () => void;
  isLoading: boolean;
}

export function HeroSection({ searchQuery, setSearchQuery, onSearch, isLoading }: HeroSectionProps) {
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      onSearch();
    }
  };

  return (
    <section className="relative overflow-hidden py-20 md:py-32">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-blue-950/20" />
      
      {/* Content */}
      <div className="container relative mx-auto px-4 text-center">
        <h1 className="mb-6 text-4xl font-bold tracking-tight md:text-5xl lg:text-6xl animate-fade-in">
          Discover the Latest Trends with{' '}
          <span className="bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
            TrendSage
          </span>
        </h1>
        
        <p className="mx-auto mb-8 max-w-2xl text-lg text-muted-foreground animate-fade-in-delay-1">
          Fetch the top headlines and AI-generated analysis on any topic.
        </p>
        
        <div className="mx-auto mb-8 flex max-w-md flex-col space-y-4 sm:flex-row sm:space-x-4 sm:space-y-0 animate-fade-in-delay-2">
          <div className="relative flex-1">
            <Input
              type="text"
              placeholder="Enter a topic..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
              className="pr-10 h-12"
            />
            <Search className="absolute right-3 top-1/2 h-5 w-5 -translate-y-1/2 transform text-muted-foreground" />
          </div>
          <Button
            onClick={onSearch}
            disabled={isLoading}
            className="h-12 px-6"
            size="lg"
          >
            Analyze Trends
          </Button>
        </div>
        
        <div className="text-sm text-muted-foreground animate-fade-in-delay-3">
          Try searching for: <span className="font-medium">AI, Crypto, Climate Change, Space Exploration</span>
        </div>
      </div>
    </section>
  );
} 