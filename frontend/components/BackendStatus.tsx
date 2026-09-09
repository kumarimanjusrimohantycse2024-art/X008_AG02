"use client";

import { useEffect, useState } from "react";

type HealthState = "checking" | "connected" | "unavailable";

const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

export function BackendStatus() {
  const [state, setState] = useState<HealthState>("checking");

  useEffect(() => {
    let active = true;
    fetch(`${backendUrl}/api/health`)
      .then((response) => {
        if (!response.ok) throw new Error("Health check failed");
        return response.json();
      })
      .then(() => active && setState("connected"))
      .catch(() => active && setState("unavailable"));
    return () => { active = false; };
  }, []);

  const label = state === "checking" ? "Checking API" : state === "connected" ? "API connected" : "API unavailable";
  return <span className="system-status"><span className={`status-dot ${state === "connected" ? "connected" : ""}`} />{label}</span>;
}
