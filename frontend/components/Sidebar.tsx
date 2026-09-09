export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">T</span><span>TalentScreen</span></div>
      <nav className="nav" aria-label="Primary navigation">
        <span className="nav-item active">Overview</span>
        <span className="nav-item">Applications</span>
        <span className="nav-item">Requirements</span>
      </nav>
      <p className="sidebar-note">Evidence-aware screening foundation<br />Version 0.1 · Local workspace</p>
    </aside>
  );
}
