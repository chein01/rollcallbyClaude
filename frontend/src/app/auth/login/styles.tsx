'use client';

import { ReactNode } from 'react';

interface AuthCardProps {
  children: ReactNode;
}

export function AuthCard({ children }: AuthCardProps) {
  return (
    <main className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-b from-white to-gray-50">
      {/* Background blur circles */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 rounded-full bg-blue-100 blur-3xl opacity-30" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 rounded-full bg-purple-100 blur-3xl opacity-30" />
      </div>

      <div className="auth-card">
        {children}
      </div>
    </main>
  );
}

export function AuthLogo() {
  return (
    <div className="flex justify-center mb-8">
      <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-500 to-purple-500 flex items-center justify-center">
        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
    </div>
  );
}

export function AuthTitle({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <>
      <h1 className="auth-title">{title}</h1>
      <p className="auth-subtitle">{subtitle}</p>
    </>
  );
}