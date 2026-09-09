"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/components/AuthProvider";

export default function LoginPage() {
  const router = useRouter();
  const { user, isLoading, login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!isLoading && user) router.replace("/");
  }, [isLoading, router, user]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      await login(email, password);
      router.replace("/");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to sign in.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="login-page">
      <section className="login-panel" aria-labelledby="login-title">
        <div className="brand"><span className="brand-mark">T</span><span>TalentScreen</span></div>
        <div className="eyebrow">Workspace access</div>
        <h1 id="login-title">Welcome back.</h1>
        <p className="login-copy">Sign in to continue to your evidence-aware screening workspace.</p>
        <form className="login-form" onSubmit={handleSubmit}>
          <label htmlFor="email">Email</label>
          <input id="email" name="email" type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} />
          <label htmlFor="password">Password</label>
          <input id="password" name="password" type="password" autoComplete="current-password" required value={password} onChange={(event) => setPassword(event.target.value)} />
          {error && <p className="form-error" role="alert">{error}</p>}
          <button className="login-button" type="submit" disabled={isSubmitting}>{isSubmitting ? "Signing in..." : "Sign in"}</button>
        </form>
      </section>
      <aside className="login-aside"><span className="pill">TalentScreen V0.3</span><p>Make candidate signals clearer. Keep the evidence trail visible.</p></aside>
    </main>
  );
}
