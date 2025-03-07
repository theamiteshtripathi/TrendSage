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
    <section className="relative overflow-hidden py-20 md:py-32">
      {/* Background elements */}
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm dark:bg-black/40 light:bg-white/10" />
      <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-black/60 dark:from-primary/10 light:from-primary/30" />
      
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
          className="mx-auto mb-8 max-w-2xl text-lg text-white/80 dark:text-white/80 light:text-gray-800"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          Fetch the top headlines and AI-generated analysis on any topic.
        </motion.p>
        
        {/* USP Feature Highlights */}
        <motion.div 
          className="mx-auto mb-10 max-w-3xl grid grid-cols-1 md:grid-cols-3 gap-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          {[
            {
              icon: <TrendingUp className="h-8 w-8 text-primary mb-2" />,
              title: "Real-time Analysis",
              description: "Get instant insights on trending topics",
              color: "from-blue-500/20 to-cyan-500/20"
            },
            {
              icon: <MessageSquare className="h-8 w-8 text-primary mb-2" />,
              title: "Chat with Trends",
              description: "Stay ahead of the game with interactive AI conversations",
              color: "from-purple-500/20 to-pink-500/20"
            },
            {
              icon: <Search className="h-8 w-8 text-primary mb-2" />,
              title: "Any Topic",
              description: "From tech to sports, we've got you covered",
              color: "from-green-500/20 to-teal-500/20"
            }
          ].map((feature, index) => (
            <motion.div
              key={index}
              className={`glass-effect p-5 rounded-xl flex flex-col items-center relative overflow-hidden border border-white/20 dark:border-white/20 light:border-primary/30 shadow-lg`}
              whileHover={{ 
                y: -5,
                boxShadow: "0 10px 25px -5px rgba(23, 145, 200, 0.3)",
                borderColor: "rgba(23, 145, 200, 0.5)"
              }}
              onHoverStart={() => setHoveredCard(index)}
              onHoverEnd={() => setHoveredCard(null)}
            >
              {/* Background gradient */}
              <div className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-30`}></div>
              
              {/* Content */}
              <div className="relative z-10">
                {feature.icon}
                <h3 className="font-semibold text-lg mb-1 dark:text-white light:text-gray-900">{feature.title}</h3>
                <p className="text-sm dark:text-white/70 light:text-gray-700 text-center">{feature.description}</p>
                
                {/* Animated arrow on hover */}
                <motion.div 
                  className="mt-3 text-primary flex items-center justify-center"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: hoveredCard === index ? 1 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <span className="text-xs mr-1">Learn more</span>
                  <ArrowRight className="h-3 w-3" />
                </motion.div>
              </div>
            </motion.div>
          ))}
        </motion.div>
        
        <motion.div 
          className="mx-auto mb-8 flex max-w-md flex-col space-y-4 sm:flex-row sm:space-x-4 sm:space-y-0"
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
              className="pr-10 h-12 bg-black/20 border-white/20 backdrop-blur-md focus:border-primary/70 focus:ring-primary/50 dark:bg-black/30 light:bg-white/60 dark:border-white/20 light:border-gray-300/50 dark:text-white light:text-gray-900 dark:placeholder-white/50 light:placeholder-gray-500 rounded-full pl-5 shadow-inner transition-all duration-300 hover:bg-black/30 dark:hover:bg-black/40 light:hover:bg-white/70 focus:shadow-[0_0_10px_rgba(23,145,200,0.3)]"
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