'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAppSelector } from '@/store';

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated } = useAppSelector((state) => state.auth);

  useEffect(() => {
    // Temporarily bypass authentication and redirect directly to dashboard
    router.push('/dashboard');
  }, [router]);

  return (
    <main className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-b from-white to-gray-50">
      <div className="text-center">
        <h1 className="text-3xl font-bold">Roll Call by AI</h1>
        <p className="mt-4">Redirecting to login page...</p>
      </div>
    </main>
  );
}
