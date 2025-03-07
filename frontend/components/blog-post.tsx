"use client"

import React, { useState } from 'react';
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

/**
 * Image Selection Mechanism:
 * 
 * 1. Keyword Extraction:
 *    - We extract keywords from both the title and content of the blog post
 *    - Common words and short words (less than 4 characters) are filtered out
 *    - This gives us a set of significant words that represent the blog's topic
 * 
 * 2. Category Mapping:
 *    - Each category has a set of predefined images mapped to specific keywords
 *    - For example, "Technology" category has images for "ai", "blockchain", "data", etc.
 *    - This creates a two-level mapping: category -> keyword -> image
 * 
 * 3. Matching Process:
 *    - First, we find the best matching category for the blog post
 *    - Then, we iterate through the extracted keywords from the content
 *    - For each keyword, we check if it matches or is included in any of the image keywords
 *    - If a match is found, we use that image
 * 
 * 4. Fallback Mechanism:
 *    - If no keyword matches are found, we use the default image for the category
 *    - This ensures every blog post has a relevant image even without exact keyword matches
 * 
 * This approach ensures that blog posts get the most contextually relevant images based on their content,
 * rather than just random images from their category.
 */

// Function to extract keywords from text with improved relevance
const extractKeywords = (text: string): string[] => {
  // Remove common words and keep only significant ones
  const commonWords = [
    'the', 'and', 'or', 'of', 'to', 'in', 'for', 'with', 'on', 'at', 'from', 'by', 
    'about', 'as', 'an', 'a', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'but', 'if', 'then', 'else', 'when',
    'up', 'down', 'out', 'in', 'that', 'this', 'these', 'those', 'it', 'its'
  ];
  
  // Extract words, remove punctuation, and filter out common words
  return text.toLowerCase()
    .replace(/[^\w\s]/g, '')
    .split(/\s+/)
    .filter(word => word.length > 3 && !commonWords.includes(word));
}

// Function to get category-specific image URLs with improved keyword matching
const getCategoryImage = (category: string, title: string, content: string = ''): string => {
  // Default images for each category with expanded keyword mappings
  const categoryImages: Record<string, Record<string, string>> = {
    'Technology': {
      'default': 'https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1000',
      'ai': 'https://images.unsplash.com/photo-1677442135136-760c813a1e2a?q=80&w=1000',
      'blockchain': 'https://images.unsplash.com/photo-1639762681057-408e52192e55?q=80&w=1000',
      'data': 'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?q=80&w=1000',
      'software': 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?q=80&w=1000',
      'hardware': 'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?q=80&w=1000',
      'cloud': 'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?q=80&w=1000',
      'security': 'https://images.unsplash.com/photo-1563013544-824ae1b704d3?q=80&w=1000'
    },
    'Tech': {
      'default': 'https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1000',
      'ai': 'https://images.unsplash.com/photo-1677442135136-760c813a1e2a?q=80&w=1000',
      'blockchain': 'https://images.unsplash.com/photo-1639762681057-408e52192e55?q=80&w=1000',
      'data': 'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?q=80&w=1000',
      'software': 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?q=80&w=1000'
    },
    'Business': {
      'default': 'https://images.unsplash.com/photo-1507679799987-c73779587ccf?q=80&w=1000',
      'finance': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=1000',
      'startup': 'https://images.unsplash.com/photo-1559136555-9303baea8ebd?q=80&w=1000',
      'market': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=1000',
      'economy': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=1000'
    },
    'Finance & Technology': {
      'default': 'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?q=80&w=1000',
      'crypto': 'https://images.unsplash.com/photo-1518546305927-5a555bb7020d?q=80&w=1000',
      'bitcoin': 'https://images.unsplash.com/photo-1518546305927-5a555bb7020d?q=80&w=1000',
      'blockchain': 'https://images.unsplash.com/photo-1639762681057-408e52192e55?q=80&w=1000',
      'fintech': 'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?q=80&w=1000'
    },
    'Health': {
      'default': 'https://images.unsplash.com/photo-1505751172876-fa1923c5c528?q=80&w=1000',
      'medical': 'https://images.unsplash.com/photo-1579154204601-01588f351e67?q=80&w=1000',
      'fitness': 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1000',
      'wellness': 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?q=80&w=1000',
      'nutrition': 'https://images.unsplash.com/photo-1490645935967-10de6ba17061?q=80&w=1000'
    },
    'Science': {
      'default': 'https://images.unsplash.com/photo-1507413245164-6160d8298b31?q=80&w=1000',
      'research': 'https://images.unsplash.com/photo-1576086213369-97a306d36557?q=80&w=1000',
      'space': 'https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?q=80&w=1000',
      'physics': 'https://images.unsplash.com/photo-1636466497217-26a8cbeaf0aa?q=80&w=1000',
      'biology': 'https://images.unsplash.com/photo-1530026405186-ed1f139313f8?q=80&w=1000'
    },
    'Sports': {
      'default': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?q=80&w=1000',
      'basketball': 'https://images.unsplash.com/photo-1546519638-68e109498ffc?q=80&w=1000',
      'football': 'https://images.unsplash.com/photo-1575361204480-aadea25e6e68?q=80&w=1000',
      'soccer': 'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?q=80&w=1000',
      'tennis': 'https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?q=80&w=1000',
      'baseball': 'https://images.unsplash.com/photo-1508344928928-7165b0c40767?q=80&w=1000',
      'celtics': 'https://images.unsplash.com/photo-1546519638-68e109498ffc?q=80&w=1000'
    },
    'Entertainment': {
      'default': 'https://images.unsplash.com/photo-1603190287605-e6ade32fa852?q=80&w=1000',
      'movie': 'https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=1000',
      'music': 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?q=80&w=1000',
      'gaming': 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?q=80&w=1000',
      'celebrity': 'https://images.unsplash.com/photo-1603190287605-e6ade32fa852?q=80&w=1000'
    },
    'Politics': {
      'default': 'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?q=80&w=1000',
      'government': 'https://images.unsplash.com/photo-1541872703-74c5e44368f9?q=80&w=1000',
      'election': 'https://images.unsplash.com/photo-1540910419892-4a36d2c3266c?q=80&w=1000',
      'policy': 'https://images.unsplash.com/photo-1575320181282-9afab399332c?q=80&w=1000',
      'trump': 'https://images.unsplash.com/photo-1580128660010-fd027e1e587a?q=80&w=1000'
    },
    'Miscellaneous': {
      'default': 'https://images.unsplash.com/photo-1523961131990-5ea7c61b2107?q=80&w=1000',
      'travel': 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?q=80&w=1000',
      'food': 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?q=80&w=1000',
      'education': 'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?q=80&w=1000',
      'art': 'https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?q=80&w=1000'
    }
  };

  // Normalize category name for matching
  const normalizedCategory = category.toLowerCase();
  
  // Find the best matching category
  const bestMatch = Object.keys(categoryImages).find(
    cat => cat.toLowerCase() === normalizedCategory
  ) || 'Miscellaneous';
  
  // Get images for the category
  const images = categoryImages[bestMatch];
  
  // Extract keywords from title and content
  const titleKeywords = extractKeywords(title);
  const contentKeywords = content ? extractKeywords(content.slice(0, 500)) : []; // Only use first 500 chars for efficiency
  const allKeywords = [...new Set([...titleKeywords, ...contentKeywords])];
  
  // Find matching image based on keywords
  for (const keyword of allKeywords) {
    for (const [key, url] of Object.entries(images)) {
      if (keyword.includes(key) || key.includes(keyword)) {
        return url;
      }
    }
  }
  
  // If no keyword match, use default image for the category
  return images['default'];
};

// Function to format content with styled headings
const formatContent = (content: string): string => {
  // Replace markdown headings (###) with styled headings
  return content.replace(/###\s+(.*?)(?:\n|$)/g, '<h3 class="text-xl font-bold text-primary mt-6 mb-3">$1</h3>');
};

// Function to get a reliable fallback image based on category
const getFallbackImage = (category: string): string => {
  const fallbackImages: Record<string, string> = {
    'Tech': '/placeholder-tech.jpg',
    'Business': '/placeholder-business.jpg',
    'Health': '/placeholder-health.jpg',
    'Science': '/placeholder-science.jpg',
    'Sports': '/placeholder-sports.jpg',
    'Entertainment': '/placeholder-entertainment.jpg',
    'Politics': '/placeholder-politics.jpg',
    'Miscellaneous': '/placeholder.jpg',
    'Finance & Technology': '/placeholder-tech.jpg',
    'default': '/placeholder.jpg'
  };
  
  return fallbackImages[category] || fallbackImages['default'];
};

// Function to validate image URL
const isValidImageUrl = (url: string): boolean => {
  if (!url) return false;
  
  // Check if URL is from a reliable source
  const reliableDomains = [
    'unsplash.com',
    'images.unsplash.com',
    'pexels.com',
    'images.pexels.com',
    'pixabay.com',
    'cdn.pixabay.com',
    'githubusercontent.com',
    'raw.githubusercontent.com',
    'cloudinary.com',
    'res.cloudinary.com'
  ];
  
  try {
    const url_obj = new URL(url);
    return reliableDomains.some(domain => url_obj.hostname.includes(domain));
  } catch (e) {
    return false;
  }
};

export function BlogPost({ title, content, category, image_url, onChatClick, onReadClick }: BlogPostProps) {
  // Safely truncate content to avoid rendering issues
  const truncatedContent = content && content.length > 200 
    ? content.slice(0, 200) + '...' 
    : content || '';

  // Extract first paragraph for description
  const description = truncatedContent.split('\n')[0];
  
  // Get a category-specific image if no image_url is provided
  const [imageError, setImageError] = useState(false);
  const fallbackImage = getFallbackImage(category);
  
  // Determine the image to display with validation
  let displayImageUrl = fallbackImage;
  if (!imageError && image_url && isValidImageUrl(image_url)) {
    displayImageUrl = image_url;
  } else if (!imageError && !image_url) {
    displayImageUrl = getCategoryImage(category, title, content);
  }

  // Handle click on the card (excluding the chat button)
  const handleCardClick = (e: React.MouseEvent) => {
    // Only trigger if the click is not on or inside the chat button
    if (!e.defaultPrevented) {
      onReadClick();
    }
  };

  return (
    <div 
      className="glass-effect rounded-xl overflow-hidden transform transition-all duration-300 hover:translate-y-[-4px] hover:shadow-xl flex flex-col h-full group cursor-pointer"
      onClick={handleCardClick}
    >
      {/* Image Section */}
      <div className="aspect-video overflow-hidden relative">
        <img
          src={displayImageUrl}
          alt={title}
          className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
          onError={(e) => {
            // If the image fails to load, try the category-specific image
            if (!imageError) {
              setImageError(true);
              (e.target as HTMLImageElement).src = fallbackImage;
            }
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent opacity-70"></div>
        <span className="absolute bottom-3 left-3 inline-block px-3 py-1 text-xs font-semibold rounded-full bg-primary/80 text-white backdrop-blur-sm">
          {category}
        </span>
      </div>
      
      {/* Content Section */}
      <div className="p-5 flex-1 flex flex-col">
        <h2 className="text-xl font-bold line-clamp-2 mb-2 group-hover:text-primary transition-colors duration-300">{title}</h2>
        
        <p className="text-muted-foreground text-sm mb-4 line-clamp-3">
          {description}
        </p>
        
        <div className="mt-auto flex space-x-2">
          <Button 
            onClick={(e) => {
              e.stopPropagation(); // Prevent card click
              onReadClick();
            }}
            className="flex-1 flex items-center justify-center space-x-1 btn-futuristic"
            size="sm"
          >
            <BookOpen className="h-4 w-4 mr-1" />
            <span>Read</span>
          </Button>
          
          <Button 
            onClick={(e) => {
              e.preventDefault(); // Prevent card click
              e.stopPropagation(); // Prevent card click
              onChatClick();
            }}
            variant="outline"
            className="flex-1 flex items-center justify-center space-x-1 border-primary/50 hover:bg-primary/20 transition-all duration-300"
            size="sm"
          >
            <MessageSquare className="h-4 w-4 mr-1" />
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
  
  // Format content with styled headings
  const formattedContent = formatContent(safeContent);
  
  // Get a category-specific image if no image_url is provided
  const displayImageUrl = image_url || getCategoryImage(category, title, content);

  return (
    <div className="glass-effect rounded-xl overflow-hidden">
      {/* Hero Image */}
      <div className="w-full h-64 md:h-96 overflow-hidden relative">
        <img
          src={displayImageUrl}
          alt={title}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent opacity-70"></div>
        <div className="absolute bottom-0 left-0 w-full p-6 md:p-8">
          <span className="inline-block px-3 py-1 text-xs font-semibold rounded-full bg-primary/80 text-white backdrop-blur-sm mb-3">
            {category}
          </span>
          <h1 className="text-3xl md:text-5xl font-bold text-white drop-shadow-lg">{title}</h1>
        </div>
      </div>
      
      <div className="p-6 md:p-8">
        <div className="prose dark:prose-invert max-w-none">
          <div dangerouslySetInnerHTML={{ __html: formattedContent.replace(/\n/g, '<br/>') }} />
        </div>
      </div>
    </div>
  );
} 