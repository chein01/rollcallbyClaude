import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { ApiResponse, ErrorResponse } from '@/types/api';
import { env } from '@/config/environment';
import { toast } from 'sonner';

// Utility function for logging
const logRequest = (type: 'request' | 'response' | 'error', data: any) => {
  // Client-side logging
  if (typeof window !== 'undefined') {
    if (type === 'error') {
      console.error(`❌ ${type.toUpperCase()}:`, data);
    } else {
      console.log(`${type === 'request' ? '🚀' : '✅'} ${type.toUpperCase()}:`, data);
    }
  }

  // Server-side logging
  if (typeof window === 'undefined') {
    console.log(`[${type.toUpperCase()}]:`, JSON.stringify(data, null, 2));
  }
};

// Default Axios configuration
const defaultConfig: AxiosRequestConfig = {
  baseURL: env.API_BASE_URL,
  timeout: env.API_TIMEOUT,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
  proxy: false
};

// ApiService class to manage API requests
class ApiService {
  private api: AxiosInstance;

  constructor(config: AxiosRequestConfig = {}) {
    this.api = axios.create({
      ...defaultConfig,
      ...config,
    });

    // Request interceptor
    this.api.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        // Add token if exists
        const token = localStorage.getItem('token');
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // Log request details
        const fullUrl = `${config.baseURL}${config.url}`;
        const requestData = {
          url: fullUrl,
          method: config.method?.toUpperCase(),
          headers: config.headers,
          data: config.data
        };
        logRequest('request', requestData);

        return config;
      },
      (error: AxiosError) => {
        const errorData = {
          message: error.message,
          details: error
        };
        logRequest('error', errorData);
        toast.error(error.message || 'Request failed');
        return Promise.reject({
          success: false,
          error: errorData
        });
      }
    );

    // Response interceptor
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        // Log response details
        const responseData = {
          url: `${response.config.baseURL}${response.config.url}`,
          status: response.status,
          data: response.data
        };
        logRequest('response', responseData);

        // Show success message if exists
        if (response.data?.message) {
          toast.success(response.data.message);
        }
        return {
          ...response,
          data: {
            success: true,
            data: response.data
          }
        };
      },
      (error: AxiosError<ErrorResponse>) => {
        // Log error details
        const errorData = {
          url: `${error.config?.baseURL}${error.config?.url}`,
          status: error.response?.status,
          message: error.response?.data?.message || error.message,
          data: error.response?.data,
          stack: error.stack
        };
        logRequest('error', errorData);

        // Handle common errors
        if (error.response?.status === 401) {
          // Handle token expiration
          localStorage.removeItem('token');
          window.location.href = '/login';
          toast.error('Session expired. Please login again.');
        } else {
          // Show error message from API response
          const errorMessage = error.response?.data?.detail || // FastAPI error format
            error.response?.data?.message ||  // Custom API error format
            error.message ||                  // Axios error message
            'Something went wrong. Please try again.';
          toast.error(errorMessage);
        }

        return Promise.reject({
          success: false,
          error: {
            message: error.response?.data?.detail ||
              error.response?.data?.message ||
              error.message,
            status: error.response?.status,
            data: error.response?.data
          }
        });
      }
    );
  }

  // API methods
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.api.get(url, config);
      return response.data;
    } catch (error) {
      return error as ApiResponse<T>;
    }
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.api.post(url, data, config);
      return response.data;
    } catch (error) {
      return error as ApiResponse<T>;
    }
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.api.put(url, data, config);
      return response.data;
    } catch (error) {
      return error as ApiResponse<T>;
    }
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.api.delete(url, config);
      return response.data;
    } catch (error) {
      return error as ApiResponse<T>;
    }
  }

  // Method to change baseURL dynamically
  setBaseUrl(baseURL: string) {
    this.api.defaults.baseURL = baseURL;
  }
}

// Export default instance
export const apiService = new ApiService();

// Export class to create new instance with different config
export default ApiService;