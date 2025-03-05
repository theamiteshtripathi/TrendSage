'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '../../lib/supabase';
import Dashboard from '../../components/Dashboard';

export default function DashboardPage() {
  const router = useRouter();

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (!session) {
        router.push('/');
      }
    });
  }, [router]);

  return <Dashboard />;
} 