import type { User } from "../types/auth";

const BASE_URL = import.meta.env.VITE_API_URL ?? "/api";
const TOKEN_KEY = "workmate_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export async function fetchCurrentUser(): Promise<User> {
  const token = getToken();
  const res = await fetch(`${BASE_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Not authenticated");
  return res.json();
}

export async function getGoogleAuthUrl(): Promise<string> {
  const res = await fetch(`${BASE_URL}/auth/google`);
  if (!res.ok) throw new Error("Failed to get auth URL");
  const data = await res.json();
  return data.authorization_url;
}

export async function logout(): Promise<void> {
  const token = getToken();
  await fetch(`${BASE_URL}/auth/logout`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  clearToken();
}
