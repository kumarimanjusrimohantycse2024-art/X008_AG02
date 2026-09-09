import { BackendStatus } from "@/components/BackendStatus";
import { Sidebar } from "@/components/Sidebar";

const foundationAreas = [
  ["Evidence first", "A future home for traceable candidate claims and source-aware assessments."],
  ["Modular by design", "A small, clear foundation for requirements, applications, and screening services."],
  ["Ready to extend", "PostgreSQL and pgvector-ready architecture without premature AI complexity."],
];

export default function Home() {
  return (
    <div className="dashboard-shell">
      <Sidebar />
      <main className="main">
        <header className="topbar">
          <div><div className="eyebrow">Workspace overview</div><h2 className="topbar-title">System foundation</h2></div>
          <BackendStatus />
        </header>
        <section className="hero">
          <span className="pill">Foundation V0.1</span>
          <h1>TalentScreen</h1>
          <p>Evidence-aware talent screening, designed to make candidate signals clearer and decisions more accountable.</p>
        </section>
        <section className="foundation-grid" aria-label="Foundation areas">
          {foundationAreas.map(([title, description]) => <article className="foundation-card" key={title}><h2>{title}</h2><p>{description}</p></article>)}
        </section>
      </main>
    </div>
  );
}
