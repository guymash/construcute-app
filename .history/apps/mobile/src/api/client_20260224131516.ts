import { useAuth } from "@src/store/useAuth";

const DEFAULT_BASE_URL = "http://localhost:8000";

export function getBaseUrl(): string {
  return DEFAULT_BASE_URL;
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const state = useAuth.getState();
  const baseUrl = getBaseUrl();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };

  if (state.token) {
    headers["Authorization"] = `Bearer ${state.token}`;
  }

  const res = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Request failed: ${res.status} ${text}`);
  }

  return (await res.json()) as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path, { method: "GET" }),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) })
};

