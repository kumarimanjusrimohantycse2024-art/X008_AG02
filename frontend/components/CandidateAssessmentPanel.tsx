"use client";

import { useEffect, useState } from "react";

import { assessCandidate, getCandidateAssessment, type CandidateAssessment, type RequirementAssessment } from "@/lib/api";

type Props = { token: string | null; applicationId: string };

const recommendationLabels: Record<CandidateAssessment["recommendation"], string> = {
  STRONG_MATCH: "Strong Match",
  GOOD_MATCH: "Good Match",
  MIXED_MATCH: "Mixed Match",
  WEAK_MATCH: "Weak Match",
};

function statusLabel(status: RequirementAssessment["status"]): string {
  return status.replaceAll("_", " ");
}

function RequirementRows({ requirements }: { requirements: RequirementAssessment[] }) {
  return <div className="candidate-requirement-list">{requirements.map((requirement) => <article className="candidate-requirement" key={requirement.requirement_id}><div><strong>{requirement.name}</strong><span>{statusLabel(requirement.status)}</span></div><div><span>{requirement.evidence_strength} evidence</span>{requirement.confidence !== null && <span>Confidence {Math.round(requirement.confidence * 100)}%</span>}</div></article>)}</div>;
}

export function CandidateAssessmentPanel({ token, applicationId }: Props) {
  const [assessment, setAssessment] = useState<CandidateAssessment | null>(null);
  const [isAssessing, setIsAssessing] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) return;
    getCandidateAssessment(token, applicationId).then(setAssessment).catch(() => setAssessment(null));
  }, [applicationId, token]);

  async function runAssessment() {
    if (!token) return;
    setIsAssessing(true);
    setError("");
    try {
      setAssessment(await assessCandidate(token, applicationId));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to assess candidate.");
    } finally {
      setIsAssessing(false);
    }
  }

  return <section className="candidate-assessment"><div className="section-heading"><div><span className="eyebrow">Candidate assessment</span><h2>Overall assessment</h2></div><button className="primary-button" onClick={runAssessment} disabled={isAssessing}>{isAssessing ? "Assessing..." : assessment ? "Refresh assessment" : "Assess candidate"}</button></div>{error && <p className="form-error" role="alert">{error}</p>}{!assessment ? <p className="assessment-empty">Run assessment after V0.6 evidence analysis is complete.</p> : <><div className="assessment-summary"><div><span className="eyebrow">Recommendation</span><strong>{recommendationLabels[assessment.recommendation]}</strong></div><div><span className="eyebrow">Required coverage</span><strong>{assessment.required_coverage.met} / {assessment.required_coverage.total} met</strong></div><div><span className="eyebrow">Preferred coverage</span><strong>{assessment.preferred_coverage.met} / {assessment.preferred_coverage.total} met</strong></div><div><span className="eyebrow">Evidence quality</span><strong>{assessment.evidence_quality.label}</strong></div></div><div className="candidate-assessment-columns"><section><div className="section-heading"><h3>Required requirements</h3></div><RequirementRows requirements={assessment.required_requirements} /></section><section><div className="section-heading"><h3>Preferred requirements</h3></div><RequirementRows requirements={assessment.preferred_requirements} /></section></div><div className="candidate-narrative-grid"><section><div className="section-heading"><h3>Strengths</h3></div>{assessment.strengths.map((item) => <article className="candidate-narrative" key={item.title}><strong>{item.title}</strong><p>{item.description}</p></article>)}</section><section><div className="section-heading"><h3>Weaknesses</h3></div>{assessment.weaknesses.map((item) => <article className="candidate-narrative" key={`${item.title}-${item.assessment_ids.join("-")}`}><strong>{item.title}</strong><p>{item.description}</p></article>)}</section></div>{assessment.tradeoffs.length > 0 && <section className="tradeoff-list"><div className="section-heading"><h3>Trade-offs</h3></div>{assessment.tradeoffs.map((tradeoff) => <article className="tradeoff-card" key={tradeoff.title}><span className="eyebrow">Trade-off</span><strong>{tradeoff.title}</strong><p><b>Advantage:</b> {tradeoff.advantage}</p><p><b>Limitation:</b> {tradeoff.limitation}</p></article>)}</section>}</>}</section>;
}
