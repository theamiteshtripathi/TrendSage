"use client"

import Link from "next/link";
import Image from "next/image";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { Button } from "@/components/ui/button";

interface HeaderProps {
  categories: string[];
  activeCategory: string;
  onCategoryClick: (category: string) => void;
}

export function Header({ categories, activeCategory, onCategoryClick }: HeaderProps) {
  return (
    <header className="border-b border-white/10 bg-black/30 backdrop-blur-md supports-[backdrop-filter]:bg-black/20 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-3">
        <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
          <div className="flex items-center space-x-4">
            <Link href="/" className="flex items-center space-x-2">
              <div className="transition-transform hover:scale-105">
                <Image 
                  src="/tslogo.png" 
                  alt="TrendSage Logo" 
                  width={40} 
                  height={40} 
                  className="h-10 w-auto"
                />
              </div>
              <span className="text-xl font-bold tracking-tight gradient-text">
                TrendSage
              </span>
            </Link>
          </div>
          
          <div className="flex items-center space-x-1 overflow-x-auto pb-2 md:pb-0 scrollbar-hide">
            {categories.map((category) => (
              <Button
                key={category}
                variant={activeCategory === category ? "default" : "ghost"}
                onClick={() => onCategoryClick(category)}
                className={`px-3 py-1.5 text-sm rounded-full whitespace-nowrap transition-all duration-300 ${
                  activeCategory === category 
                    ? "bg-primary text-white shadow-lg shadow-primary/20" 
                    : "hover:bg-primary/20 hover:text-primary"
                }`}
                size="sm"
              >
                {category}
              </Button>
            ))}
          </div>
          
          <div className="flex items-center space-x-4">
            <Link href="/pricing" className="text-sm font-medium hover:text-primary transition-colors">
              Pricing
            </Link>
            <ThemeToggle />
          </div>
        </div>
      </div>
    </header>
  );
} 