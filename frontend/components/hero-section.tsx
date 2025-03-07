"use client"

import React, { useState } from 'react';
import { Search, MessageSquare, TrendingUp, ArrowRight } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';

interface HeroSectionProps {
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  onSearch: () => void;
  isLoading: boolean;
}

export function HeroSection({ searchQuery, setSearchQuery, onSearch, isLoading }: HeroSectionProps) {
  const [hoveredCard, setHoveredCard] = useState<number | null>(null);

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      onSearch();
    }
  };

  return (
    <section className="hero-bg w-full overflow-hidden py-20 md:py-32">
      {/* Background elements */}
      <div className="absolute inset-0 backdrop-blur-sm dark:bg-black/40 light:bg-white/40" />
      <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent dark:to-black/60 light:to-white/60" />
      
      {/* Animated circles */}
      <div className="absolute -left-20 -top-20 h-80 w-80 rounded-full bg-primary/10 blur-3xl animate-pulse" />
      <div className="absolute -right-20 -bottom-20 h-80 w-80 rounded-full bg-primary/10 blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      
      {/* Content */}
      <div className="container relative mx-auto px-4 text-center z-10">
        <motion.h1 
          className="mb-6 text-4xl font-bold tracking-tight md:text-5xl lg:text-6xl"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          Discover the Latest Trends with{' '}
          <span className="gradient-text">
            TrendSage
          </span>
        </motion.h1>
        
        <motion.p 
          className="mx-auto mb-8 max-w-2xl text-lg dark:text-white/80 light:text-gray-700"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          Fetch the top headlines and AI-generated analysis on any topic.
        </motion.p>
        
        {/* Feature highlights */}
        <motion.div 
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 max-w-5xl mx-auto"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          {/* Feature cards */}
          {[
            {
              title: 'Real-time Analysis',
              description: 'Get instant insights on trending topics',
              icon: <TrendingUp className="h-8 w-8 text-primary mb-2" />,
            },
            {
              title: 'Chat with Trends',
              description: 'Stay ahead of the game with interactive AI conversations',
              icon: <MessageSquare className="h-8 w-8 text-primary mb-2" />,
            },
            {
              title: 'Any Topic',
              description: 'From tech to sports, we\'ve got you covered',
              icon: <Search className="h-8 w-8 text-primary mb-2" />,
            }
          ].map((feature, index) => (
            <div 
              key={index}
              className="relative p-6 rounded-xl backdrop-blur-md dark:bg-black/30 light:bg-white/60 border dark:border-white/10 light:border-gray-200/50 transition-all duration-300 hover:shadow-xl hover:shadow-primary/5 hover:border-primary/30 overflow-hidden group"
              onMouseEnter={() => setHoveredCard(index)}
              onMouseLeave={() => setHoveredCard(null)}
            >
              <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <div className="relative z-10">
                {feature.icon}
                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                <p className="dark:text-white/70 light:text-gray-700 mb-4">{feature.description}</p>
                <div className={`flex items-center text-primary transition-opacity duration-300 ${hoveredCard === index ? 'opacity-100' : 'opacity-0'}`}>
                  <span className="mr-1 text-sm font-medium">Learn more</span>
                  <ArrowRight className="h-4 w-4 animate-pulse" />
                </div>
              </div>
            </div>
          ))}
        </motion.div>
        
        {/* Search bar */}
        <motion.div 
          className="flex flex-col sm:flex-row gap-4 max-w-2xl mx-auto"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <div className="relative flex-1">
            <Input
              type="text"
              placeholder="Enter a topic..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
              className="pr-10 h-12 dark:bg-black/20 light:bg-white/80 dark:border-white/20 light:border-gray-300/50 backdrop-blur-md focus:border-primary/70 focus:ring-primary/50 dark:text-white light:text-gray-900 dark:placeholder-white/50 light:placeholder-gray-500 rounded-full pl-5 shadow-inner transition-all duration-300 hover:bg-black/30 dark:hover:bg-black/40 light:hover:bg-white/90 focus:shadow-[0_0_10px_rgba(23,145,200,0.3)]"
            />
            <Search className="absolute right-3 top-1/2 h-5 w-5 -translate-y-1/2 transform text-primary animate-pulse" />
          </div>
          <Button
            onClick={onSearch}
            disabled={isLoading}
            className="h-12 px-6 btn-futuristic rounded-full shadow-lg hover:shadow-primary/20 transition-all duration-300 hover:translate-y-[-2px]"
            size="lg"
          >
            <span>Analyze Trends</span>
          </Button>
        </motion.div>
        
        <motion.div 
          className="text-sm text-white/60 dark:text-white/60 light:text-gray-700"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          Try searching for: <span className="font-medium text-primary/80">AI, Crypto, Climate Change, Space Exploration</span>
        </motion.div>
      </div>
    </section>
  );
} 