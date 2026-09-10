"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { WorkspaceShell } from "@/components/WorkspaceShell";
import { useAuth } from "@/components/AuthProvider";
import { getApplications, getJobs, type Application, type Job } from "@/lib/api";

type ApplicationSummary = Application & { job_title: string };

export default function ApplicationsInboxPage() {
  const { token } = useAuth();
  const [applications, setApplications] = useState<ApplicationSummary[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    getJobs(token).then(async (jobs) => {
      const applicationGroups = await Promise.all(jobs.map(async (job: Job) => (await getApplications(token, job.id)).map((application) => ({ ...application, job_title: job.title }))));
      setApplications(applicationGroups.flat());
    }).catch((caught) => setError(caught instanceof Error ? caught.message : "Unable to load applications.")).finally(() => setLoading(false));
  }, [token]);

  return <WorkspaceShell eyebrow="Recruiting workspace" title="Applications"><div className="page-heading"><div><span className="eyebrow">Candidate pipeline</span><h1>Applications</h1><p>Review candidate applications across your authorized jobs.</p></div><Link className="secondary-button" href="/jobs">View jobs</Link></div>{error && <p className="form-error" role="alert">{error}</p>}{loading ? <p className="loading-copy">Loading applications...</p> : applications.length === 0 ? <section className="empty-state"><h2>No applications yet.</h2><p>Applications uploaded to your jobs will appear here.</p><Link className="primary-button" href="/jobs">Open job library</Link></section> : <section className="application-list">{applications.map((application) => <Link className="application-card" href={`/applications/${application.id}`} key={application.id}><div><span className="job-status">{application.ingestion_status}</span><h2>{application.candidate_name}</h2><p>{application.job_title} · {application.candidate_email || "No email provided"}</p></div><div className="application-meta"><span>{application.document_count} documents</span><span>{application.chunk_count} chunks</span><span>{application.status}</span></div></Link>)}</section>}</WorkspaceShell>;
}
