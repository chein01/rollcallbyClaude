'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAppDispatch } from '@/store';
import { setCredentials, setLoading, setError } from '@/store/slices/authSlice';
import { AuthCard, AuthLogo, AuthTitle } from './styles';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const dispatch = useAppDispatch();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    dispatch(setLoading(true));

    try {
      // TODO: Implement actual login logic here with API call
      // Example:
      // const response = await loginUser({ email, password });
      // dispatch(setCredentials(response));
      
      // For now, simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      router.push('/today');
    } catch (error) {
      console.error('Login failed:', error);
      dispatch(setError('Login failed. Please check your credentials.'));
    } finally {
      setIsLoading(false);
      dispatch(setLoading(false));
    }
  };

  return (
    <AuthCard>
      <AuthLogo />
      <AuthTitle 
        title="Welcome Back" 
        subtitle="Sign in to continue to Roll Call" 
      />

      {/* Login Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <input
            type="email"
            placeholder="Email"
            className="input-field"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <input
            type="password"
            placeholder="Password"
            className="input-field"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <div className="pt-2">
          <button
            type="submit"
            className="auth-button"
            disabled={isLoading}
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </div>
      </form>

      {/* Additional Links */}
      <div className="mt-6 text-center space-y-2">
        <button
          onClick={() => router.push('/forgot-password')}
          className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
        >
          Forgot Password?
        </button>
        <div className="flex items-center justify-center space-x-1">
          <span className="text-sm text-gray-500">Don't have an account?</span>
          <button
            onClick={() => router.push('/auth/register')}
            className="text-sm text-blue-500 hover:text-blue-700 font-medium transition-colors"
          >
            Sign Up
          </button>
        </div>
      </div>
    </AuthCard>
  );
}