"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { useAuth } from "@/components/AuthProvider";
import { WorkspaceShell } from "@/components/WorkspaceShell";
import { getApplication, getApplicationChunks, type Application, type Chunk, type Document } from "@/lib/api";

export default function ApplicationDetailPage() {
  const params = useParams<{ applicationId: string }>();
  const { token } = useAuth();
  const [application, setApplication] = useState<(Application & { documents: Document[] }) | null>(null);
  const [chunks, setChunks] = useState<Chunk[]>([]);
  const [error, setError] = useState("");
  useEffect(() => { if (!token) return; Promise.all([getApplication(token, params.applicationId), getApplicationChunks(token, params.applicationId)]).then(([loadedApplication, loadedChunks]) => { setApplication(loadedApplication); setChunks(loadedChunks); }).catch((caught) => setError(caught instanceof Error ? caught.message : "Unable to load application.")); }, [params.applicationId, token]);
  return <WorkspaceShell eyebrow="Source inspection" title={application?.candidate_name ?? "Application detail"}>{error ? <p className="form-error" role="alert">{error}</p> : !application ? <p className="loading-copy">Loading application...</p> : <section className="detail-page"><div className="detail-header"><div><span className="job-status">{application.ingestion_status}</span><h1>{application.candidate_name}</h1><p>{application.candidate_email || "No email provided"}</p></div><Link className="secondary-button" href={`/jobs/${application.job_id}/applications`}>Back to applications</Link></div><div className="detail-grid"><article className="detail-panel"><span className="eyebrow">Documents</span>{application.documents.map((document) => <div className="document-row" key={document.id}><div><strong>{document.document_type === "COVER_LETTER" ? "Cover letter" : "Resume"}</strong><p>{document.file_name} · {Math.ceil(document.file_size / 1024)} KB</p></div><span>{document.chunk_count} chunks</span></div>)}</article><article className="detail-panel"><span className="eyebrow">Processing</span><div className="count-row"><strong>{application.document_count}</strong><span>Documents</span></div><div className="count-row"><strong>{application.chunk_count}</strong><span>Chunks</span></div></article></div><section className="chunk-list"><div className="section-heading"><h2>Source chunks</h2><span>Embeddings are not generated in V0.5</span></div>{chunks.map((chunk) => <article className="chunk-card" key={chunk.id}><header><span>Chunk {chunk.chunk_index + 1}</span><span>{chunk.section || "Unclassified section"}{chunk.page_number ? ` · Page ${chunk.page_number}` : ""}</span></header><p>{chunk.text}</p></article>)}</section></section>}</WorkspaceShell>;
}
