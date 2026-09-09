"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { BackendStatus } from "@/components/BackendStatus";
import { Sidebar } from "@/components/Sidebar";
import { useAuth } from "@/components/AuthProvider";

export function WorkspaceShell({ title, eyebrow, children }: Readonly<{ title: string; eyebrow: string; children: React.ReactNode }>) {
  const router = useRouter();
  const { user, isLoading, logout } = useAuth();

  useEffect(() => {
    if (!isLoading && !user) router.replace("/login");
  }, [isLoading, router, user]);

  if (isLoading || !user) return <main className="auth-loading">Loading workspace...</main>;
  return <div className="dashboard-shell"><Sidebar user={user} onLogout={() => { logout(); router.replace("/login"); }} /><main className="main"><header className="topbar"><div><div className="eyebrow">{eyebrow}</div><h2 className="topbar-title">{title}</h2></div><BackendStatus /></header>{children}</main></div>;
}
