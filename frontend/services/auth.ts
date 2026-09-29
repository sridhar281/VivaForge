import { apiClient } from "@/lib/api-client";
import type { LoginPayload, RegisterPayload, TokenResponse, UserRead } from "@/types/auth";

const TOKEN_STORAGE_KEY = "vivaforge_token";

export function saveToken(token: string): void {
  window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearToken(): void {
  window.localStorage.removeItem(TOKEN_STORAGE_KEY);
}

export async function register(payload: RegisterPayload): Promise<UserRead> {
  const { data } = await apiClient.post<UserRead>("/auth/register", payload);
  return data;
}

export async function login(payload: LoginPayload): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>("/auth/login", payload);
  saveToken(data.access_token);
  return data;
}

export async function getCurrentUser(): Promise<UserRead> {
  const { data } = await apiClient.get<UserRead>("/auth/me");
  return data;
}

export function logout(): void {
  clearToken();
}
