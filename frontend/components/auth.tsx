import { useState } from 'react'
import { supabase } from '@/lib/supabase'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { FaGoogle, FaGithub } from 'react-icons/fa'

export default function AuthComponent() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isSignUp, setIsSignUp] = useState(false)
  const [message, setMessage] = useState<string | null>(null)

  const handleEmailSignIn = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setMessage(null)

    try {
      const { error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (error) throw error
    } catch (error: any) {
      setError(error.message || 'An error occurred during sign in')
    } finally {
      setLoading(false)
    }
  }

  const handleEmailSignUp = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setMessage(null)

    try {
      const { error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          emailRedirectTo: typeof window !== 'undefined' ? window.location.origin : '',
        },
      })

      if (error) throw error
      setMessage('Check your email for the confirmation link')
    } catch (error: any) {
      setError(error.message || 'An error occurred during sign up')
    } finally {
      setLoading(false)
    }
  }

  const handleOAuthSignIn = async (provider: 'google' | 'github') => {
    setLoading(true)
    setError(null)
    
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo: typeof window !== 'undefined' ? window.location.origin : '',
        },
      })
      
      if (error) throw error
    } catch (error: any) {
      setError(error.message || `An error occurred during ${provider} sign in`)
      setLoading(false)
    }
  }

  const handlePasswordReset = async () => {
    if (!email) {
      setError('Please enter your email address')
      return
    }
    
    setLoading(true)
    setError(null)
    setMessage(null)
    
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: typeof window !== 'undefined' ? window.location.origin : '',
      })
      
      if (error) throw error
      setMessage('Check your email for the password reset link')
    } catch (error: any) {
      setError(error.message || 'An error occurred during password reset')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="w-full max-w-[450px] mx-auto p-6 rounded-xl backdrop-blur-md bg-black/30 border border-white/10 shadow-xl">
      <div className="flex flex-col items-center mb-8">
        <div className="relative w-16 h-16 mb-2">
          <Image 
            src="/tslogo.png" 
            alt="TrendSage Logo" 
            fill
            className="object-contain"
          />
        </div>
        <h1 className="text-3xl font-bold gradient-text">TrendSage</h1>
        <p className="text-muted-foreground mt-1">AI-Powered Trend Analysis</p>
      </div>

      {error && (
        <div className="bg-red-500/20 border border-red-500/50 text-red-200 px-4 py-2 rounded-md mb-4">
          {error}
        </div>
      )}

      {message && (
        <div className="bg-green-500/20 border border-green-500/50 text-green-200 px-4 py-2 rounded-md mb-4">
          {message}
        </div>
      )}

      <form onSubmit={isSignUp ? handleEmailSignUp : handleEmailSignIn} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">Email address</Label>
          <Input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your.email@example.com"
            required
            className="h-11 bg-black/40 border-white/20 focus:border-primary/70 transition-all duration-200 backdrop-blur-sm"
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
            className="h-11 bg-black/40 border-white/20 focus:border-primary/70 transition-all duration-200 backdrop-blur-sm"
          />
        </div>

        <Button 
          type="submit" 
          disabled={loading}
          className="w-full h-11 bg-gradient-to-r from-[#1791c8] to-[#1a73e8] hover:from-[#1a73e8] hover:to-[#1791c8] transition-all duration-300"
        >
          {loading ? 'Loading...' : isSignUp ? 'Sign Up' : 'Sign In'}
        </Button>
      </form>

      <div className="mt-4 text-center">
        <button
          onClick={() => setIsSignUp(!isSignUp)}
          className="text-sm text-primary hover:underline"
        >
          {isSignUp ? 'Already have an account? Sign In' : 'Don\'t have an account? Sign Up'}
        </button>
      </div>

      {!isSignUp && (
        <div className="mt-2 text-center">
          <button
            onClick={handlePasswordReset}
            className="text-sm text-muted-foreground hover:text-primary hover:underline"
          >
            Forgot your password?
          </button>
        </div>
      )}

      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-white/10"></div>
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-background px-2 text-muted-foreground">Or continue with</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Button
          type="button"
          variant="outline"
          onClick={() => handleOAuthSignIn('google')}
          disabled={loading}
          className="h-11 bg-black/40 border-white/20 hover:bg-white/10 transition-all duration-200"
        >
          <FaGoogle className="mr-2" />
          Google
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={() => handleOAuthSignIn('github')}
          disabled={loading}
          className="h-11 bg-black/40 border-white/20 hover:bg-white/10 transition-all duration-200"
        >
          <FaGithub className="mr-2" />
          GitHub
        </Button>
      </div>
    </div>
  )
} 