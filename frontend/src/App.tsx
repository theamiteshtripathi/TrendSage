import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom'
import { Session } from '@supabase/supabase-js'
import { supabase } from './lib/supabase'
import Auth from './components/Auth'
import Dashboard from './components/Dashboard'

function App() {
  const [session, setSession] = useState<Session | null>(null)

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
    })

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
    })

    return () => subscription.unsubscribe()
  }, [])

  return (
    <Router>
      <div className="app">
        <Routes>
          <Route
            path="/"
            element={
              !session ? (
                <Auth />
              ) : (
                <Navigate to="/dashboard" replace />
              )
            }
          />
          <Route
            path="/dashboard"
            element={
              session ? (
                <Dashboard />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />
        </Routes>
      </div>
      <style jsx>{`
        .app {
          min-height: 100vh;
          background: #f7f7f7;
        }
      `}</style>
    </Router>
  )
}

export default App 