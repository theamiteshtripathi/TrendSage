import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API endpoints
export const endpoints = {
  analyzeTrends: '/api/analyze-trends',
  blogs: '/api/blogs',
  trends: '/api/trends',
  categories: '/api/categories',
};

// API functions
export const apiClient = {
  // Analyze trends for a given topic
  analyzeTrends: async (topic: string, category?: string) => {
    const response = await api.post(endpoints.analyzeTrends, { topic, category });
    return response.data;
  },

  // Get all blogs
  getBlogs: async (category?: string) => {
    const params = category ? { category } : {};
    const response = await api.get(endpoints.blogs, { params });
    return response.data;
  },

  // Get all trends
  getTrends: async (category?: string) => {
    const params = category ? { category } : {};
    const response = await api.get(endpoints.trends, { params });
    return response.data;
  },

  // Get all categories
  getCategories: async () => {
    const response = await api.get(endpoints.categories);
    return response.data;
  },
}; 