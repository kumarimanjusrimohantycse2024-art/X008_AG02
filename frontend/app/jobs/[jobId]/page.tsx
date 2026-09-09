"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { WorkspaceShell } from "@/components/WorkspaceShell";
import { useAuth } from "@/components/AuthProvider";
import { getJob, type Job } from "@/lib/api";

export default function JobDetailPage() {
  const params = useParams<{ jobId: string }>();
  const { token } = useAuth();
  const [job, setJob] = useState<Job | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { if (!token) return; getJob(token, params.jobId).then(setJob).catch((caught) => setError(caught instanceof Error ? caught.message : "Job not found.")); }, [params.jobId, token]);
  return <WorkspaceShell eyebrow="Requisition detail" title={job?.title ?? "Job detail"}>{error ? <p className="form-error" role="alert">{error}</p> : !job ? <p className="loading-copy">Loading job...</p> : <section className="detail-page"><div className="detail-header"><div><span className="job-status">{job.status}</span><h1>{job.title}</h1><p>{job.department || "Unassigned department"}</p></div><div className="form-actions"><Link className="secondary-button" href="/jobs">Back to jobs</Link><Link className="primary-button" href={`/jobs/${job.id}/requirements`}>Review requirements</Link></div></div><div className="detail-grid"><article className="detail-panel"><span className="eyebrow">Description</span><p className="description-text">{job.description}</p></article><article className="detail-panel"><span className="eyebrow">Requirement coverage</span><div className="count-row"><strong>{job.required_count}</strong><span>Required</span></div><div className="count-row"><strong>{job.preferred_count}</strong><span>Preferred</span></div></article></div></section>}</WorkspaceShell>;
}
