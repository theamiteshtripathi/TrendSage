"use client"

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/header";
import { Button } from "@/components/ui/button";
import { Check } from "lucide-react";

// Sample categories for the navigation bar
const categories = ["All", "Tech", "Business", "Health", "Science", "Sports", "Entertainment", "Politics", "Miscellaneous"];

export default function PricingPage() {
  const router = useRouter();
  const [activeCategory, setActiveCategory] = useState("All");
  const [billingCycle, setBillingCycle] = useState<"monthly" | "yearly">("monthly");

  const handleCategoryClick = (category: string) => {
    setActiveCategory(category);
    if (category === "All") {
      router.push("/");
    } else {
      router.push(`/category/${encodeURIComponent(category)}`);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header 
        categories={categories} 
        activeCategory={activeCategory} 
        onCategoryClick={handleCategoryClick} 
      />

      <main className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">Pricing</h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Choose the plan that works for you
          </p>
        </div>

        {/* Billing Toggle */}
        <div className="flex justify-center mb-12">
          <div className="glass-effect inline-flex rounded-full p-1">
            <button
              onClick={() => setBillingCycle("monthly")}
              className={`px-6 py-2 rounded-full text-sm font-medium transition-all ${
                billingCycle === "monthly"
                  ? "bg-primary text-white shadow-lg"
                  : "text-muted-foreground hover:text-white"
              }`}
            >
              MONTHLY
            </button>
            <button
              onClick={() => setBillingCycle("yearly")}
              className={`px-6 py-2 rounded-full text-sm font-medium transition-all ${
                billingCycle === "yearly"
                  ? "bg-primary text-white shadow-lg"
                  : "text-muted-foreground hover:text-white"
              }`}
            >
              YEARLY (SAVE 20%)
            </button>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid gap-8 md:grid-cols-3">
          {/* Free Plan */}
          <div className="glass-effect rounded-2xl overflow-hidden border border-white/10 transition-all hover:border-primary/30 hover:shadow-lg hover:shadow-primary/10">
            <div className="p-8">
              <h3 className="text-lg font-medium mb-2">Hobby</h3>
              <div className="mb-6">
                <span className="text-5xl font-bold">Free</span>
              </div>
              
              <div className="border-t border-white/10 my-6"></div>
              
              <h4 className="font-medium mb-4">Includes</h4>
              <ul className="space-y-3 mb-8">
                <li className="flex items-start">
                  <Check className="h-5 w-5 text-primary mr-2 shrink-0" />
                  <span>Pro two-week trial</span>
                </li>
                <li className="flex items-start">
                  <Check className="h-5 w-5 text-primary mr-2 shrink-0" />
                  <span>2000 completions</span>
                </li>
                <li className="flex items-start">
                  <Check className="h-5 w-5 text-primary mr-2 shrink-0" />
                  <span>50 slow premium requests</span>
                </li>
              </ul>
              
              <Button className="w-full btn-futuristic">
                <span>Get Started</span>
              </Button>
            </div>
          </div>
          
          {/* Pro Plan */}
          <div className="glass-effect rounded-2xl overflow-hidden border border-primary/30 shadow-lg shadow-primary/10 relative">
            {/* Gradient background */}
            <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-purple-500/10 to-pink-500/20 opacity-30"></div>
            
            <div className="p-8 relative">
              <h3 className="text-lg font-medium mb-2">Pro</h3>
              <div className="mb-6">
                <span className="text-5xl font-bold">${billingCycle === "monthly" ? "20" : "16"}</span>
                <span className="text-muted-foreground ml-1">/month</span>
              </div>
              
              <div className="border-t border-white/10 my-6"></div>
              
              <h4 className="font-medium mb-4">Everything in Hobby, plus</h4>
              <ul className="space-y-3 mb-8">
                <li className="flex items-start">
                  <Check className="h-5 w-5 text-primary mr-2 shrink-0" />
                  <span>Unlimited completions</span>
                </li>
                <li className="flex items-start">
                  <Check className="h-5 w-5 text-primary mr-2 shrink-0" />
                  <span>500 fast premium requests per month</span>
                </li>
                <li className="flex items-start">
                  <Check className="h-5 w-5 text-primary mr-2 shrink-0" />
                  <span>Unlimited slow premium requests</span>
                </li>
              </ul>
              
              <Button className="w-full btn-futuristic">
                <span>Get Started</span>
              </Button>
            </div>
          </div>
          
          {/* Business Plan */}
          <div className="glass-effect rounded-2xl overflow-hidden border border-white/10 transition-all hover:border-primary/30 hover:shadow-lg hover:shadow-primary/10">
            <div className="p-8">
              <h3 className="text-lg font-medium mb-2">Business</h3>
              <div className="mb-6">
                <span className="text-5xl font-bold">${billingCycle === "monthly" ? "40" : "32"}</span>
                <span className="text-muted-foreground ml-1">/user/month</span>
              </div>
              
              <div className="border-t border-white/10 my-6"></div>
              
              <h4 className="font-medium mb-4">Everything in Pro, plus</h4>
              <ul className="space-y-3 mb-8">
                <li className="flex items-start">
                  <Check className="h-5 w-5 text-primary mr-2 shrink-0" />
                  <span>Enforce privacy mode org-wide</span>
                </li>
                <li className="flex items-start">
                  <Check className="h-5 w-5 text-primary mr-2 shrink-0" />
                  <span>Centralized team billing</span>
                </li>
                <li className="flex items-start">
                  <Check className="h-5 w-5 text-primary mr-2 shrink-0" />
                  <span>Admin dashboard with usage stats</span>
                </li>
                <li className="flex items-start">
                  <Check className="h-5 w-5 text-primary mr-2 shrink-0" />
                  <span>SAML/OIDC SSO</span>
                </li>
              </ul>
              
              <Button className="w-full btn-futuristic">
                <span>Get Started</span>
              </Button>
            </div>
          </div>
        </div>
        
        {/* Enterprise Section */}
        <div className="mt-16 text-center">
          <p className="text-lg mb-4">
            Questions about enterprise security, procurement, or custom contracts?
          </p>
          <Button variant="outline" className="border-primary/50 hover:bg-primary/20 transition-all duration-300">
            Contact Sales
          </Button>
        </div>
      </main>
    </div>
  );
} 