import type { AuthUser } from "@/lib/api";
import Link from "next/link";

export function Sidebar({ user, onLogout }: { user: AuthUser; onLogout: () => void }) {
  return (
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">T</span><span>TalentScreen</span></div>
      <nav className="nav" aria-label="Primary navigation">
        <Link className="nav-item active" href="/">Overview</Link>
        <Link className="nav-item" href="/jobs">Jobs</Link>
        <span className="nav-item">Applications</span>
      </nav>
      <div className="sidebar-account"><strong>{user.name}</strong><span>{user.role}</span><button type="button" onClick={onLogout}>Sign out</button></div>
      <p className="sidebar-note">Evidence-aware screening workspace<br />Version 0.4 · Local workspace</p>
    </aside>
  );
}
