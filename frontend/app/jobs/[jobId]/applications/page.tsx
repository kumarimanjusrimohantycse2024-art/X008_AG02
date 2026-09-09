"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { useAuth } from "@/components/AuthProvider";
import { WorkspaceShell } from "@/components/WorkspaceShell";
import { getApplications, getJob, type Application, type Job } from "@/lib/api";

export default function ApplicationsPage() {
  const params = useParams<{ jobId: string }>();
  const { token } = useAuth();
  const [job, setJob] = useState<Job | null>(null);
  const [applications, setApplications] = useState<Application[]>([]);
  const [error, setError] = useState("");
  useEffect(() => { if (!token) return; Promise.all([getJob(token, params.jobId), getApplications(token, params.jobId)]).then(([loadedJob, loadedApplications]) => { setJob(loadedJob); setApplications(loadedApplications); }).catch((caught) => setError(caught instanceof Error ? caught.message : "Unable to load applications.")); }, [params.jobId, token]);
  return <WorkspaceShell eyebrow="Application intake" title={job?.title ?? "Applications"}>{error ? <p className="form-error" role="alert">{error}</p> : !job ? <p className="loading-copy">Loading applications...</p> : <section className="detail-page"><div className="page-heading"><div><span className="eyebrow">Source material</span><h1>Applications</h1><p>Candidate documents are processed into traceable source chunks.</p></div><div className="form-actions"><Link className="secondary-button" href={`/jobs/${job.id}`}>Back to job</Link><Link className="primary-button" href={`/jobs/${job.id}/applications/new`}>Upload application</Link></div></div>{applications.length === 0 ? <section className="empty-state"><h2>No applications yet.</h2><p>Upload a resume and optional cover letter to begin source processing.</p></section> : <section className="application-list">{applications.map((application) => <Link className="application-card" href={`/applications/${application.id}`} key={application.id}><div><span className="job-status">{application.ingestion_status}</span><h2>{application.candidate_name}</h2><p>{application.candidate_email || "No email provided"}</p></div><div className="application-meta"><span>{application.document_count} documents</span><span>{application.chunk_count} chunks</span><span>{application.status}</span></div></Link>)}</section>}</section>}</WorkspaceShell>;
}
