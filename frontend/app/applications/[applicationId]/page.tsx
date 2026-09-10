"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { useAuth } from "@/components/AuthProvider";
import { CandidateAssessmentPanel } from "@/components/CandidateAssessmentPanel";
import { WorkspaceShell } from "@/components/WorkspaceShell";
import { analyzeApplicationEvidence, extractApplicationClaims, getApplication, getApplicationChunks, getApplicationClaims, type Application, type Claim, type Chunk, type Document, type EvidenceAssessment } from "@/lib/api";

export default function ApplicationDetailPage() {
  const params = useParams<{ applicationId: string }>();
  const { token } = useAuth();
  const [application, setApplication] = useState<(Application & { documents: Document[] }) | null>(null);
  const [chunks, setChunks] = useState<Chunk[]>([]);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [assessments, setAssessments] = useState<EvidenceAssessment[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => { if (!token) return; Promise.all([getApplication(token, params.applicationId), getApplicationChunks(token, params.applicationId), getApplicationClaims(token, params.applicationId)]).then(([loadedApplication, loadedChunks, loadedClaims]) => { setApplication(loadedApplication); setChunks(loadedChunks); setClaims(loadedClaims); }).catch((caught) => setError(caught instanceof Error ? caught.message : "Unable to load application.")); }, [params.applicationId, token]);

  async function runEvidenceAnalysis() {
    if (!token) return;
    setIsAnalyzing(true);
    setError("");
    try {
      const extractedClaims = await extractApplicationClaims(token, params.applicationId);
      setClaims(extractedClaims);
      setAssessments(await analyzeApplicationEvidence(token, params.applicationId));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to analyze application evidence.");
    } finally {
      setIsAnalyzing(false);
    }
  }

  return <WorkspaceShell eyebrow="Evidence intelligence" title={application?.candidate_name ?? "Application detail"}>{application && <CandidateAssessmentPanel token={token} applicationId={application.id} />}{error ? <p className="form-error" role="alert">{error}</p> : !application ? <p className="loading-copy">Loading application...</p> : <section className="detail-page"><div className="detail-header"><div><span className="job-status">{application.ingestion_status}</span><h1>{application.candidate_name}</h1><p>{application.candidate_email || "No email provided"}</p></div><div className="detail-actions"><button className="primary-button" onClick={runEvidenceAnalysis} disabled={isAnalyzing}>{isAnalyzing ? "Analyzing..." : "Run evidence analysis"}</button><Link className="secondary-button" href={`/jobs/${application.job_id}/applications`}>Back to applications</Link></div></div><div className="detail-grid"><article className="detail-panel"><span className="eyebrow">Documents</span>{application.documents.map((document) => <div className="document-row" key={document.id}><div><strong>{document.document_type === "COVER_LETTER" ? "Cover letter" : "Resume"}</strong><p>{document.file_name} · {Math.ceil(document.file_size / 1024)} KB</p></div><span>{document.chunk_count} chunks</span></div>)}</article><article className="detail-panel"><span className="eyebrow">Processing</span><div className="count-row"><strong>{application.document_count}</strong><span>Documents</span></div><div className="count-row"><strong>{application.chunk_count}</strong><span>Chunks</span></div><div className="count-row"><strong>{claims.length}</strong><span>Claims</span></div></article></div>{assessments.length > 0 && <section className="evidence-section"><div className="section-heading"><h2>Requirement assessments</h2><span>Evidence is limited to this application</span></div><div className="assessment-list">{assessments.map((assessment) => <article className="assessment-card" key={assessment.requirement_id}><header><strong>{assessment.status.replaceAll("_", " ")}</strong><span>{assessment.evidence_strength} evidence · {Math.round(assessment.confidence * 100)}% confidence</span></header><p>{assessment.claim_summary}</p><small>{assessment.evidence_summary}</small></article>)}</div></section>}{claims.length > 0 && <section className="evidence-section"><div className="section-heading"><h2>Candidate claims</h2><span>Each claim keeps its source reference</span></div><div className="claim-list">{claims.map((claim) => <article className="claim-card" key={claim.id}><div><span className="eyebrow">{claim.claim_type}</span><p>{claim.text}</p></div><span className="claim-source">{claim.source_chunk_id ? "Source linked" : "No source"}</span></article>)}</div></section>}<section className="chunk-list"><div className="section-heading"><h2>Source chunks</h2><span>Original text remains inspectable</span></div>{chunks.map((chunk) => <article className="chunk-card" key={chunk.id}><header><span>Chunk {chunk.chunk_index + 1}</span><span>{chunk.section || "Unclassified section"}{chunk.page_number ? ` · Page ${chunk.page_number}` : ""}</span></header><p>{chunk.text}</p></article>)}</section></section>}</WorkspaceShell>;
}
