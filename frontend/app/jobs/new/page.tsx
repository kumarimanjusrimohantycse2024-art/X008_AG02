"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { WorkspaceShell } from "@/components/WorkspaceShell";
import { useAuth } from "@/components/AuthProvider";
import { analyzeRequirements, createJob, type Requirement } from "@/lib/api";

export default function NewJobPage() {
  const router = useRouter();
  const { token } = useAuth();
  const [title, setTitle] = useState("");
  const [department, setDepartment] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  async function submit(event: FormEvent) { event.preventDefault(); if (!token) return; setError(""); setLoading(true); try { const job = await createJob(token, { title, department, description }); const analysis = await analyzeRequirements(token, job.id); sessionStorage.setItem(`talentscreen-draft-${job.id}`, JSON.stringify(analysis.requirements as Requirement[])); router.push(`/jobs/${job.id}/requirements`); } catch (caught) { setError(caught instanceof Error ? caught.message : "Unable to analyze requirements."); } finally { setLoading(false); } }
  return <WorkspaceShell eyebrow="New requisition" title="Create a job"><section className="form-page"><div className="page-heading"><div><span className="eyebrow">Step 01</span><h1>Start with the requisition.</h1><p>Describe the role in your own words. Suggestions remain editable until you save them.</p></div></div><form className="job-form" onSubmit={submit}><label htmlFor="title">Job title</label><input id="title" required value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Backend Software Engineer" /><label htmlFor="department">Department</label><input id="department" value={department} onChange={(event) => setDepartment(event.target.value)} placeholder="Engineering" /><label htmlFor="description">Job description</label><textarea id="description" required minLength={1} rows={12} value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Required:\n- Python backend development\n\nPreferred:\n- Docker" />{error && <p className="form-error" role="alert">{error}</p>}<div className="form-actions"><button className="secondary-button" type="button" onClick={() => router.push("/jobs")}>Cancel</button><button className="primary-button" type="submit" disabled={loading}>{loading ? "Analyzing requirements..." : "Analyze requirements"}</button></div></form></section></WorkspaceShell>;
}
