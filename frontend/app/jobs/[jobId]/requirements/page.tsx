"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { WorkspaceShell } from "@/components/WorkspaceShell";
import { useAuth } from "@/components/AuthProvider";
import { analyzeRequirements, getJob, saveRequirements, type Job, type Requirement } from "@/lib/api";

const blankRequirement = (): Requirement => ({ name: "", description: "", priority: "REQUIRED", minimum_years: null, weight: 1, aliases: [], evidence_expectations: {} });

export default function RequirementsPage() {
  const params = useParams<{ jobId: string }>();
  const router = useRouter();
  const { token } = useAuth();
  const [job, setJob] = useState<Job | null>(null);
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [loading, setLoading] = useState(true);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => { if (!token) return; const draft = sessionStorage.getItem(`talentscreen-draft-${params.jobId}`); getJob(token, params.jobId).then(setJob).then(() => { if (draft) setRequirements(JSON.parse(draft) as Requirement[]); else return analyzeRequirements(token, params.jobId).then((result) => setRequirements(result.requirements)); }).catch((caught) => setError(caught instanceof Error ? caught.message : "Unable to load requirements.")).finally(() => setLoading(false)); }, [params.jobId, token]);
  function update(index: number, field: keyof Requirement, value: unknown) { setRequirements((current) => current.map((item, itemIndex) => itemIndex === index ? { ...item, [field]: value } : item)); }
  async function save() { if (!token) return; setWorking(true); setError(""); try { await saveRequirements(token, params.jobId, requirements); sessionStorage.removeItem(`talentscreen-draft-${params.jobId}`); router.push(`/jobs/${params.jobId}`); } catch (caught) { setError(caught instanceof Error ? caught.message : "Unable to save requirements."); } finally { setWorking(false); } }
  async function reanalyze() { if (!token) return; setWorking(true); setError(""); try { const result = await analyzeRequirements(token, params.jobId); setRequirements(result.requirements); } catch (caught) { setError(caught instanceof Error ? caught.message : "Requirement analysis is currently unavailable."); } finally { setWorking(false); } }
  return <WorkspaceShell eyebrow="Requirement review" title={job?.title ?? "Requirements"}>{loading ? <p className="loading-copy">Loading requirements...</p> : <section className="review-page"><div className="page-heading"><div><span className="pill">AI suggestions are editable</span><h1>Review requirements.</h1><p>Recruiter edits are the final source of truth. Nothing is saved until you confirm.</p></div><button className="secondary-button" type="button" onClick={reanalyze} disabled={working}>Re-analyze</button></div>{error && <p className="form-error" role="alert">{error}</p>}<div className="requirement-columns">{(["REQUIRED", "PREFERRED"] as const).map((priority) => <section className="requirement-section" key={priority}><div className="section-heading"><h2>{priority === "REQUIRED" ? "Required requirements" : "Preferred requirements"}</h2><span>{requirements.filter((item) => item.priority === priority).length}</span></div>{requirements.map((requirement, index) => requirement.priority === priority && <article className="requirement-editor" key={`${requirement.id ?? requirement.name}-${index}`}><div className="editor-row"><input aria-label="Requirement name" value={requirement.name} onChange={(event) => update(index, "name", event.target.value)} /><button type="button" className="text-button" onClick={() => setRequirements((current) => current.filter((_, itemIndex) => itemIndex !== index))}>Delete</button></div><textarea aria-label="Requirement description" rows={2} value={requirement.description} onChange={(event) => update(index, "description", event.target.value)} /><div className="editor-grid"><label>Minimum years<input type="number" min="0" step="0.5" value={requirement.minimum_years ?? ""} onChange={(event) => update(index, "minimum_years", event.target.value ? Number(event.target.value) : null)} /></label><label>Weight<input type="number" min="0.01" step="0.1" value={requirement.weight} onChange={(event) => update(index, "weight", Number(event.target.value))} /></label></div><p className="editor-meta">Aliases: {requirement.aliases.length ? requirement.aliases.join(", ") : "None"}</p><p className="editor-meta">Evidence expectation: {String(requirement.evidence_expectations.notes ?? "Defined by the requisition")}</p></article>)}</section>)}</div><div className="form-actions review-actions"><button className="secondary-button" type="button" onClick={() => setRequirements((current) => [...current, blankRequirement()])}>Add requirement</button><button className="primary-button" type="button" onClick={save} disabled={working || requirements.length === 0}>{working ? "Saving..." : "Save finalized requirements"}</button></div></section>}</WorkspaceShell>;
}
