"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { WorkspaceShell } from "@/components/WorkspaceShell";
import { useAuth } from "@/components/AuthProvider";
import { getJobs, type Job } from "@/lib/api";

export default function JobsPage() {
  const { token } = useAuth();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  useEffect(() => { if (!token) return; getJobs(token).then(setJobs).catch((caught) => setError(caught instanceof Error ? caught.message : "Unable to load jobs.")).finally(() => setLoading(false)); }, [token]);
  return <WorkspaceShell eyebrow="Recruiting workspace" title="Jobs"><div className="page-heading"><div><span className="eyebrow">Requisitions</span><h1>Job library</h1><p>Shape a clear requisition before applications arrive.</p></div><Link className="primary-button" href="/jobs/new">Create job</Link></div>{error && <p className="form-error" role="alert">{error}</p>}{loading ? <p className="loading-copy">Loading jobs...</p> : jobs.length === 0 ? <section className="empty-state"><h2>No jobs yet.</h2><p>Create your first requisition to begin reviewing requirements.</p><Link className="primary-button" href="/jobs/new">Create your first job</Link></section> : <section className="job-grid">{jobs.map((job) => <Link className="job-card" href={`/jobs/${job.id}`} key={job.id}><span className="job-status">{job.status}</span><h2>{job.title}</h2><p>{job.department || "Unassigned department"}</p><div className="job-meta"><span>{job.required_count} required</span><span>{job.preferred_count} preferred</span></div></Link>)}</section>}</WorkspaceShell>;
}
