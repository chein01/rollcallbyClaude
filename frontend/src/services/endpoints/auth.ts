import { apiService } from '../api';
import { AuthResponse } from '@/types/api';

export interface LoginPayload {
    email: string;
    password: string;
}

export interface SignUpPayload {
    username: string;
    email: string;
    password: string;
    full_name: string;
}

export const authApi = {
    login: (data: LoginPayload) =>
        apiService.post<AuthResponse>('auth/login', data),

    signUp: (data: SignUpPayload) =>
        apiService.post<AuthResponse>('v1/users', data),

    logout: () =>
        apiService.post<void>('auth/logout'),

    getCurrentUser: () =>
        apiService.get<AuthResponse['user']>('auth/me'),
}; 