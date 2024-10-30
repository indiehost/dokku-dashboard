import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Wrapper for API requests
export async function apiRequest(endpoint: string, options: RequestInit = {}) {

  // use dokku api url from .env.local
  const baseUrl = import.meta.env.VITE_DOKKU_API_URL || 'http://localhost:8000';
  const url = `${baseUrl}${endpoint}`;

  const headers = new Headers({
    'Content-Type': 'application/json',
    ...options.headers,
  });

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.statusText}`);
  }

  return response.json();
}
