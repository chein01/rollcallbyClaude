'use client';

import Link from 'next/link';
import { useAppSelector } from '@/store';
import { ThemeToggle } from './ThemeToggle';
import { Logo } from './Logo';

export default function Header() {
  const { user } = useAppSelector((state) => state.auth);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 max-w-screen-2xl items-center">
        <div className="mr-4 flex">
          <Link href="/" className="mr-6 flex items-center space-x-2">
            <Logo />
          </Link>
        </div>

        <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
          <nav className="flex items-center space-x-6">
            {user && (
              <>
                <Link href="/events" className="text-sm font-medium text-foreground/60 transition-colors hover:text-foreground">
                  Events
                </Link>
                <Link href="/checkin" className="text-sm font-medium text-foreground/60 transition-colors hover:text-foreground">
                  Today Check-in
                </Link>
                <Link href="/user/profile" className="text-sm font-medium text-foreground/60 transition-colors hover:text-foreground">
                  Profile
                </Link>
              </>
            )}
          </nav>
          <div className="flex items-center space-x-4">
            <ThemeToggle />
            {!user && (
              <Link 
                href="/auth/login"
                className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4"
              >
                Login
              </Link>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}