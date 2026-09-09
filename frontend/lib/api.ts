export type UserRole = "ADMIN" | "RECRUITER";

export type AuthUser = {
  id: string;
  email: string;
  name: string;
  role: UserRole;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: AuthUser;
};

export type JobStatus = "DRAFT" | "READY" | "SCREENING" | "COMPLETED" | "ARCHIVED";
export type RequirementPriority = "REQUIRED" | "PREFERRED";
export type Job = { id: string; title: string; department: string | null; description: string; status: JobStatus; created_by: string; created_at: string; required_count: number; preferred_count: number };
export type Requirement = { id?: string; name: string; description: string; priority: RequirementPriority; minimum_years: number | null; weight: number; aliases: string[]; evidence_expectations: Record<string, unknown> };
export type RequirementAnalysis = { requirements: Requirement[]; source: string };
export type Application = { id: string; job_id: string; candidate_id: string; candidate_name: string; candidate_email: string | null; candidate_phone: string | null; status: string; ingestion_status: string; screening_status: string; submitted_at: string | null; created_at: string; document_count: number; chunk_count: number };
export type Document = { id: string; document_type: "RESUME" | "COVER_LETTER" | "OTHER"; file_name: string; mime_type: string; file_size: number; sha256: string; raw_text: string | null; created_at: string; chunk_count: number };
export type Chunk = { id: string; document_id: string; chunk_index: number; section: string | null; text: string; page_number: number | null; created_at: string };
export type Claim = { id: string; application_id: string; text: string; claim_type: string; source_chunk_id: string | null };
export type EvidenceAssessment = { application_id: string; requirement_id: string; status: "MET" | "PARTIALLY_MET" | "UNSUPPORTED" | "NOT_FOUND"; evidence_strength: "STRONG" | "MODERATE" | "WEAK" | "NONE"; confidence: number; claim_summary: string; evidence_summary: string; reasoning: string; evidence_refs: string[] };

const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${backendUrl}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(body?.detail ?? "Unable to sign in.");
  }
  return response.json() as Promise<LoginResponse>;
}

export async function getCurrentUser(token: string): Promise<AuthUser> {
  const response = await fetch(`${backendUrl}/api/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Authentication expired.");
  return response.json() as Promise<AuthUser>;
}

export async function authenticatedFetch(path: string, token: string, init?: RequestInit): Promise<Response> {
  const headers = new Headers(init?.headers);
  headers.set("Authorization", `Bearer ${token}`);
  return fetch(`${backendUrl}${path}`, { ...init, headers });
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(body?.detail ?? "Request failed.");
  }
  return response.json() as Promise<T>;
}

export async function getJobs(token: string): Promise<Job[]> {
  return parseResponse<Job[]>(await authenticatedFetch("/api/jobs", token));
}

export async function getJob(token: string, jobId: string): Promise<Job> {
  return parseResponse<Job>(await authenticatedFetch(`/api/jobs/${jobId}`, token));
}

export async function createJob(token: string, payload: { title: string; department: string; description: string }): Promise<Job> {
  return parseResponse<Job>(await authenticatedFetch("/api/jobs", token, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }));
}

export async function updateJob(token: string, jobId: string, payload: Partial<Pick<Job, "title" | "department" | "description" | "status">>): Promise<Job> {
  return parseResponse<Job>(await authenticatedFetch(`/api/jobs/${jobId}`, token, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }));
}

export async function analyzeRequirements(token: string, jobId: string): Promise<RequirementAnalysis> {
  return parseResponse<RequirementAnalysis>(await authenticatedFetch(`/api/jobs/${jobId}/requirements/analyze`, token, { method: "POST" }));
}

export async function saveRequirements(token: string, jobId: string, requirements: Requirement[]): Promise<Requirement[]> {
  return parseResponse<Requirement[]>(await authenticatedFetch(`/api/jobs/${jobId}/requirements`, token, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ requirements }) }));
}

export async function createApplication(token: string, jobId: string, fields: { candidateName: string; candidateEmail: string; candidatePhone: string; resume: File; coverLetter?: File }): Promise<Application & { documents: Document[] }> {
  const body = new FormData();
  body.append("candidate_name", fields.candidateName);
  body.append("candidate_email", fields.candidateEmail);
  body.append("candidate_phone", fields.candidatePhone);
  body.append("resume", fields.resume);
  if (fields.coverLetter) body.append("cover_letter", fields.coverLetter);
  return parseResponse<Application & { documents: Document[] }>(await authenticatedFetch(`/api/jobs/${jobId}/applications`, token, { method: "POST", body }));
}

export async function getApplications(token: string, jobId: string): Promise<Application[]> {
  return parseResponse<Application[]>(await authenticatedFetch(`/api/jobs/${jobId}/applications`, token));
}

export async function getApplication(token: string, applicationId: string): Promise<Application & { documents: Document[] }> {
  return parseResponse<Application & { documents: Document[] }>(await authenticatedFetch(`/api/applications/${applicationId}`, token));
}

export async function getApplicationChunks(token: string, applicationId: string): Promise<Chunk[]> {
  return parseResponse<Chunk[]>(await authenticatedFetch(`/api/applications/${applicationId}/chunks`, token));
}

export async function getApplicationClaims(token: string, applicationId: string): Promise<Claim[]> {
  return parseResponse<Claim[]>(await authenticatedFetch(`/api/applications/${applicationId}/claims`, token));
}

export async function extractApplicationClaims(token: string, applicationId: string): Promise<Claim[]> {
  return parseResponse<Claim[]>(await authenticatedFetch(`/api/applications/${applicationId}/extract-claims`, token, { method: "POST" }));
}

export async function analyzeApplicationEvidence(token: string, applicationId: string): Promise<EvidenceAssessment[]> {
  return parseResponse<EvidenceAssessment[]>(await authenticatedFetch(`/api/applications/${applicationId}/analyze-evidence`, token, { method: "POST" }));
}
