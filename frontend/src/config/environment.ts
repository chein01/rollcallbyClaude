// Define interface for environment variables
export interface Environment {
    API_BASE_URL: string;
    API_VERSION: string;
    API_TIMEOUT: number;
    ENV: string;
}

// Get environment variables from Next.js process.env
export const env: Environment = {
    API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/",
    API_VERSION: process.env.NEXT_PUBLIC_API_VERSION || "v1",
    API_TIMEOUT: Number(process.env.NEXT_PUBLIC_API_TIMEOUT) || 30000,
    ENV: process.env.NEXT_PUBLIC_ENV || "development",
};
