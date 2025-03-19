'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAppDispatch } from '@/store';
import { setCredentials, setLoading, setError } from '@/store/slices/authSlice';
import { AuthCard, AuthLogo, AuthTitle } from '../login/styles';
import { authApi } from '@/services/endpoints/auth';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
    confirmPassword: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const dispatch = useAppDispatch();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      dispatch(setError('Passwords do not match'));
      return;
    }

    setIsLoading(true);
    dispatch(setLoading(true));

    try {
      const response = await authApi.signUp({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name
      });

      if (response.success && response.data) {
        // Save login info to Redux store
        dispatch(setCredentials(response.data));

        // Redirect after successful registration
        router.push('/auth/login');
      } else {
        dispatch(setError('Registration failed. Please try again.'));
      }
    } catch (error: any) {
      console.error('Registration failed:', error);
      dispatch(setError(error.response?.data?.message || 'Registration failed. Please try again.'));
    } finally {
      setIsLoading(false);
      dispatch(setLoading(false));
    }
  };

  return (
    <AuthCard>
      <div className="max-w-md w-full space-y-8">
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
              name="username"
              placeholder="Username"
              className="input-field"
              value={formData.username}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <input
              type="text"
              name="full_name"
              placeholder="Full Name"
              className="input-field"
              value={formData.full_name}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <input
              type="email"
              name="email"
              placeholder="Email"
              className="input-field"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <input
              type="password"
              name="password"
              placeholder="Password"
              className="input-field"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <input
              type="password"
              name="confirmPassword"
              placeholder="Confirm Password"
              className="input-field"
              value={formData.confirmPassword}
              onChange={handleChange}
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
      </div>
    </AuthCard>
  );
}