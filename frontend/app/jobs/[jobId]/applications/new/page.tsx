"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { ChangeEvent, FormEvent, useState } from "react";

import { useAuth } from "@/components/AuthProvider";
import { WorkspaceShell } from "@/components/WorkspaceShell";
import { createApplication } from "@/lib/api";

const maxBytes = 10 * 1024 * 1024;
const allowedTypes = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"];

export default function NewApplicationPage() {
  const params = useParams<{ jobId: string }>();
  const router = useRouter();
  const { token } = useAuth();
  const [candidateName, setCandidateName] = useState("");
  const [candidateEmail, setCandidateEmail] = useState("");
  const [candidatePhone, setCandidatePhone] = useState("");
  const [resume, setResume] = useState<File | null>(null);
  const [coverLetter, setCoverLetter] = useState<File | undefined>();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const validateFile = (file: File | undefined, required: boolean): string => { if (!file) return required ? "Resume is required." : ""; if (!allowedTypes.includes(file.type)) return "Only PDF and DOCX files are supported."; if (file.size > maxBytes) return "Files must be 10 MB or smaller."; return ""; };
  const onFileChange = (event: ChangeEvent<HTMLInputElement>, setter: (file: File | undefined) => void, required: boolean) => { const file = event.target.files?.[0]; const message = validateFile(file, required); setError(message); if (!message) setter(file); };
  const submit = async (event: FormEvent) => { event.preventDefault(); const fileError = validateFile(resume ?? undefined, true) || validateFile(coverLetter, false); if (!candidateName.trim() || fileError) { setError(fileError || "Candidate name is required."); return; } if (!token || !resume) return; setLoading(true); setError(""); try { const application = await createApplication(token, params.jobId, { candidateName, candidateEmail, candidatePhone, resume, coverLetter }); router.push(`/applications/${application.id}`); } catch (caught) { setError(caught instanceof Error ? caught.message : "Application processing failed."); } finally { setLoading(false); } };
  return <WorkspaceShell eyebrow="Application intake" title="Upload application"><section className="form-page"><div className="page-heading"><div><span className="eyebrow">Candidate source material</span><h1>New application</h1><p>Upload a resume and optional cover letter for deterministic text processing.</p></div><Link className="secondary-button" href={`/jobs/${params.jobId}/applications`}>Cancel</Link></div><form className="job-form" onSubmit={submit}><label htmlFor="candidate-name">Candidate name *</label><input id="candidate-name" value={candidateName} onChange={(event) => setCandidateName(event.target.value)} required /><label htmlFor="candidate-email">Candidate email</label><input id="candidate-email" type="email" value={candidateEmail} onChange={(event) => setCandidateEmail(event.target.value)} /><label htmlFor="candidate-phone">Candidate phone</label><input id="candidate-phone" value={candidatePhone} onChange={(event) => setCandidatePhone(event.target.value)} /><label htmlFor="resume">Resume * <span className="field-hint">PDF or DOCX, max 10 MB</span></label><input id="resume" type="file" accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" onChange={(event) => onFileChange(event, (file) => setResume(file ?? null), true)} required /><label htmlFor="cover-letter">Cover letter <span className="field-hint">Optional PDF or DOCX</span></label><input id="cover-letter" type="file" accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" onChange={(event) => onFileChange(event, setCoverLetter, false)} />{error && <p className="form-error" role="alert">{error}</p>}<div className="form-actions"><button className="primary-button" type="submit" disabled={loading}>{loading ? "Processing documents..." : "Create application"}</button></div></form></section></WorkspaceShell>;
}
