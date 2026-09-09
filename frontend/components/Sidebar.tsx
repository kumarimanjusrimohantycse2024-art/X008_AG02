import type { AuthUser } from "@/lib/api";

export function Sidebar({ user, onLogout }: { user: AuthUser; onLogout: () => void }) {
  return (
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">T</span><span>TalentScreen</span></div>
      <nav className="nav" aria-label="Primary navigation">
        <span className="nav-item active">Overview</span>
        <span className="nav-item">Applications</span>
        <span className="nav-item">Requirements</span>
      </nav>
      <div className="sidebar-account"><strong>{user.name}</strong><span>{user.role}</span><button type="button" onClick={onLogout}>Sign out</button></div>
      <p className="sidebar-note">Evidence-aware screening workspace<br />Version 0.3 · Local workspace</p>
    </aside>
  );
}
