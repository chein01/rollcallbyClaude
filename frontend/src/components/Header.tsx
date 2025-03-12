'use client';

import Link from 'next/link';
import { useAppSelector } from '@/store';
import { useRouter } from 'next/navigation';

export default function Header() {
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);
  const router = useRouter();

  return (
    <header className="bg-white shadow-sm py-4">
      <div className="container mx-auto px-4 flex justify-between items-center">
        <Link href="/dashboard" className="text-xl font-bold text-blue-600 hover:text-blue-800 transition-colors">
          RollCallByCusor
        </Link>
        
        <div>
          {isAuthenticated && user ? (
            <div className="relative group">
              <button 
                onClick={() => router.push('/user/profile')} 
                className="flex items-center space-x-2 text-gray-700 hover:text-blue-600 transition-colors"
              >
                <span>{user.name}</span>
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          ) : (
            <Link 
              href="/auth/login" 
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Login
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}