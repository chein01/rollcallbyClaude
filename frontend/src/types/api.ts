// API Response Types

// Standard error response format
export interface ErrorResponse {
  message?: string;
  detail?: string;  // FastAPI error format
  code?: string;
  details?: Record<string, any>;
}

// Generic API response wrapper
export interface ApiResponse<T> {
  data?: T;
  status?: number;
  statusText?: string;
  headers?: Record<string, string>;
  success: boolean;
  error?: ErrorResponse;
}

// Pagination metadata
export interface PaginationMeta {
  currentPage: number;
  totalPages: number;
  totalItems: number;
  itemsPerPage: number;
}

// Paginated response wrapper
export interface PaginatedResponse<T> {
  items: T[];
  meta: PaginationMeta;
}

// Authentication responses
export interface AuthResponse {
  token: string;
  user: {
    id: string;
    email: string;
    name: string;
    role: string;
  };
}

// User profile
export interface UserProfile {
  id: string;
  email: string;
  name: string;
  role: string;
  createdAt: string;
  updatedAt: string;
}