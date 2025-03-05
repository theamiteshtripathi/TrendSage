'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '../lib/supabase';
import Auth from '../components/Auth';
import { Session } from '@supabase/supabase-js';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }: { data: { session: Session | null } }) => {
      if (session) {
        router.push('/dashboard');
      }
    });
  }, [router]);

  return (
    <main className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-4xl font-bold text-center mb-8">Welcome to News Tracker</h1>
        <div className="max-w-md mx-auto">
          <Auth />
        </div>
      </div>
    </main>
  );
} 