"use client"

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/header";
import { Button } from "@/components/ui/button";
import { Check, X, Zap } from "lucide-react";

// Sample categories for the navigation bar
const categories = ["All", "Tech", "Business", "Health", "Science", "Sports", "Entertainment", "Politics", "Miscellaneous"];

export default function PricingPage() {
  const router = useRouter();
  const [activeCategory, setActiveCategory] = useState("All");
  const [billingCycle, setBillingCycle] = useState<"monthly" | "yearly">("monthly");

  // Calculate yearly prices with 20% discount
  const getYearlyPrice = (monthlyPrice: number) => {
    return Math.floor(monthlyPrice * 12 * 0.8);
  };

  const handleCategoryClick = (category: string) => {
    setActiveCategory(category);
    if (category === "All") {
      router.push("/");
    } else {
      router.push(`/category/${encodeURIComponent(category)}`);
    }
  };

  const pricingPlans = [
    {
      name: "Free",
      description: "Perfect for casual trend watchers",
      price: 0,
      features: [
        "5 trend analyses per month",
        "Basic chat with trends",
        "Access to public trend library",
        "Standard response time",
        "Email support"
      ],
      limitations: [
        "Limited to 5 analyses per month",
        "No advanced AI insights",
        "No custom categories",
        "No priority updates"
      ],
      cta: "Get Started",
      popular: false
    },
    {
      name: "Pro",
      description: "For serious trend analysts and content creators",
      price: billingCycle === "monthly" ? 19 : getYearlyPrice(19),
      features: [
        "1,000 trend analyses per month",
        "Unlimited chat with all trends",
        "Full access to trend library",
        "Priority response time",
        "Priority email & chat support",
        "Custom categories",
        "Advanced AI insights",
        "Trend alerts",
        "Export to PDF/CSV"
      ],
      limitations: [],
      cta: "Upgrade to Pro",
      popular: true
    },
    {
      name: "Business",
      description: "Enterprise-grade trend intelligence",
      price: billingCycle === "monthly" ? 49 : getYearlyPrice(49),
      features: [
        "Unlimited trend analyses",
        "Unlimited chat with all trends",
        "Full access to trend library",
        "Fastest response time",
        "24/7 priority support",
        "Custom categories & tagging",
        "Advanced AI insights & predictions",
        "Real-time trend alerts",
        "API access",
        "Team collaboration",
        "Custom integrations",
        "Dedicated account manager"
      ],
      limitations: [],
      cta: "Contact Sales",
      popular: false
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Header 
        categories={categories} 
        activeCategory={activeCategory} 
        onCategoryClick={handleCategoryClick} 
      />
      
      <main className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold gradient-text mb-4">Choose Your Plan</h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Get unlimited access to AI-powered trend analysis and insights with our flexible pricing plans
          </p>
          
          {/* Billing toggle */}
          <div className="mt-8 inline-flex items-center p-1 dark:bg-black/30 light:bg-white/60 backdrop-blur-md rounded-full dark:border-white/10 light:border-gray-200/50 border">
            <button
              type="button"
              onClick={() => setBillingCycle("monthly")}
              className={`px-6 py-2 rounded-full transition-all ${
                billingCycle === "monthly" 
                  ? "bg-primary text-white shadow-lg" 
                  : "dark:text-white/70 light:text-gray-700 hover:text-primary"
              }`}
            >
              Monthly
            </button>
            <button
              type="button"
              onClick={() => setBillingCycle("yearly")}
              className={`px-6 py-2 rounded-full transition-all flex items-center ${
                billingCycle === "yearly" 
                  ? "bg-primary text-white shadow-lg" 
                  : "dark:text-white/70 light:text-gray-700 hover:text-primary"
              }`}
            >
              Yearly <span className="ml-2 text-xs font-bold bg-green-500/80 text-white px-2 py-0.5 rounded-full">Save 20%</span>
            </button>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {pricingPlans.map((plan) => (
            <div 
              key={plan.name}
              className={`dark:bg-black/30 light:bg-white/60 backdrop-blur-md rounded-xl overflow-hidden transition-all duration-300 hover:translate-y-[-4px] relative ${
                plan.popular ? 'border-2 border-primary/50 shadow-lg shadow-primary/20' : 'dark:border border-white/10 light:border border-gray-200/50'
              }`}
            >
              {plan.popular && (
                <div className="absolute top-0 right-0 bg-primary text-white px-4 py-1 text-sm font-bold rounded-bl-lg">
                  Most Popular
                </div>
              )}
              
              <div className="p-6">
                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                <p className="text-muted-foreground mb-6">{plan.description}</p>
                
                <div className="mb-6">
                  <span className="text-4xl font-bold">${plan.price}</span>
                  <span className="text-muted-foreground">/{billingCycle === "monthly" ? "month" : "year"}</span>
                </div>
                
                <Button 
                  className={`w-full mb-6 ${plan.popular ? 'btn-futuristic' : ''}`}
                  variant={plan.popular ? "default" : "outline"}
                >
                  {plan.popular && <Zap className="mr-2 h-4 w-4" />}
                  {plan.cta}
                </Button>
                
                <div className="space-y-4">
                  <p className="font-semibold">What's included:</p>
                  <ul className="space-y-2">
                    {plan.features.map((feature) => (
                      <li key={feature} className="flex items-start">
                        <Check className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                  
                  {plan.limitations.length > 0 && (
                    <>
                      <p className="font-semibold mt-4">Limitations:</p>
                      <ul className="space-y-2">
                        {plan.limitations.map((limitation) => (
                          <li key={limitation} className="flex items-start">
                            <X className="h-5 w-5 text-red-500 mr-2 shrink-0 mt-0.5" />
                            <span className="text-muted-foreground">{limitation}</span>
                          </li>
                        ))}
                      </ul>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-16 text-center">
          <h2 className="text-2xl font-bold mb-4">Need a custom plan?</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            We offer custom enterprise solutions for organizations with specific needs.
            Contact our sales team to discuss your requirements.
          </p>
          <Button size="lg" variant="outline" className="dark:border-primary/50 light:border-primary/50 hover:bg-primary/20">
            Contact Sales
          </Button>
        </div>
      </main>
    </div>
  );
} 