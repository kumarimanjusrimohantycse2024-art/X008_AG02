export type UserRole = "ADMIN" | "RECRUITER";

export type AuthUser = {
  id: string;
  email: string;
  name: string;
  role: UserRole;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: AuthUser;
};

const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${backendUrl}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(body?.detail ?? "Unable to sign in.");
  }
  return response.json() as Promise<LoginResponse>;
}

export async function getCurrentUser(token: string): Promise<AuthUser> {
  const response = await fetch(`${backendUrl}/api/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Authentication expired.");
  return response.json() as Promise<AuthUser>;
}

export async function authenticatedFetch(path: string, token: string, init?: RequestInit): Promise<Response> {
  const headers = new Headers(init?.headers);
  headers.set("Authorization", `Bearer ${token}`);
  return fetch(`${backendUrl}${path}`, { ...init, headers });
}
