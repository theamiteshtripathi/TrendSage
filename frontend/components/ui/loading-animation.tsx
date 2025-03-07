"use client"

import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingAnimationProps {
  message?: string;
}

export function LoadingAnimation({ message = "Hang tight while we analyze the latest trends for you..." }: LoadingAnimationProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      <div className="relative h-24 w-24 mb-6 flex items-center justify-center">
        <Loader2 className="h-16 w-16 animate-spin text-blue-600" />
      </div>
      <h3 className="text-xl font-medium mb-2">Analyzing Trends</h3>
      <p className="text-muted-foreground max-w-md">{message}</p>
    </div>
  );
}

export function SuccessAnimation({ title }: { title: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      <div className="bg-green-500 rounded-full p-3 mb-6">
        <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <h3 className="text-xl font-medium mb-2">Analysis Complete!</h3>
      <p className="text-muted-foreground max-w-md">
        We've analyzed the latest trends for <span className="font-semibold">{title}</span>
      </p>
      <div className="flex space-x-4 mt-6">
        <button className="px-4 py-2 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 transition-colors">
          Read Analysis
        </button>
        <button className="px-4 py-2 border border-blue-600 text-blue-600 rounded-md font-medium hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors">
          Chat with Trends
        </button>
      </div>
    </div>
  );
} 