"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { getCurrentUser, login as requestLogin, type AuthUser } from "@/lib/api";

type AuthContextValue = {
  user: AuthUser | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const TOKEN_KEY = "talentscreen_access_token";
const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: Readonly<{ children: React.ReactNode }>) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedToken = window.localStorage.getItem(TOKEN_KEY);
    if (!storedToken) {
      setIsLoading(false);
      return;
    }
    setToken(storedToken);
    getCurrentUser(storedToken)
      .then(setUser)
      .catch(() => {
        window.localStorage.removeItem(TOKEN_KEY);
        setToken(null);
      })
      .finally(() => setIsLoading(false));
  }, []);

  async function login(email: string, password: string) {
    const result = await requestLogin(email, password);
    window.localStorage.setItem(TOKEN_KEY, result.access_token);
    setToken(result.access_token);
    setUser(result.user);
  }

  function logout() {
    window.localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
  }

  return <AuthContext.Provider value={{ user, token, isLoading, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
