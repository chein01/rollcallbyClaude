'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAppDispatch } from '@/store';
import { setCredentials, setLoading, setError } from '@/store/slices/authSlice';
import { AuthCard, AuthLogo, AuthTitle } from '../login/styles';

export default function RegisterPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const dispatch = useAppDispatch();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate passwords match
    if (password !== confirmPassword) {
      dispatch(setError('Passwords do not match'));
      return;
    }

    setIsLoading(true);
    dispatch(setLoading(true));

    try {
      // TODO: Implement actual registration logic here with API call
      // Example:
      // const response = await registerUser({ name, email, password });
      // dispatch(setCredentials(response));
      
      // For now, simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      router.push('/today');
    } catch (error) {
      console.error('Registration failed:', error);
      dispatch(setError('Registration failed. Please try again.'));
    } finally {
      setIsLoading(false);
      dispatch(setLoading(false));
    }
  };

  return (
    <AuthCard>
      <AuthLogo />
      <AuthTitle 
        title="Create Account" 
        subtitle="Sign up to start using Roll Call" 
      />

      {/* Registration Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <input
            type="text"
            placeholder="Full Name"
            className="input-field"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
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
        <div>
          <input
            type="password"
            placeholder="Confirm Password"
            className="input-field"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
        </div>
        <div className="pt-2">
          <button
            type="submit"
            className="auth-button"
            disabled={isLoading}
          >
            {isLoading ? 'Creating Account...' : 'Create Account'}
          </button>
        </div>
      </form>

      {/* Additional Links */}
      <div className="mt-6 text-center">
        <div className="flex items-center justify-center space-x-1">
          <span className="text-sm text-gray-500">Already have an account?</span>
          <button
            onClick={() => router.push('/auth/login')}
            className="text-sm text-blue-500 hover:text-blue-700 font-medium transition-colors"
          >
            Sign In
          </button>
        </div>
      </div>
    </AuthCard>
  );
}