import axios from "axios";

/**
 * Single axios instance for all backend calls.
 * NEXT_PUBLIC_API_BASE_URL must point at the FastAPI server, e.g.
 * http://localhost:8000/api/v1 in development.
 */
export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1",
  timeout: 30_000,
});

// Attach the JWT (once auth is implemented in Phase 2) on every request.
apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = window.localStorage.getItem("vivaforge_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});
