# API Contract

V0.4 endpoints:

- `GET /` returns API identification and readiness.
- `GET /api/health` returns `{ status, service, version, database }`, preserving the V0.1 fields and adding real database status.
- `GET /api/health/database` reports a real PostgreSQL connectivity check as `connected` or `unavailable`.
- `POST /api/auth/login` accepts `{ email, password }` and returns an expiring bearer token plus safe user data.
- `GET /api/auth/me` requires a valid bearer token and returns the current user without `password_hash`.
- `GET /api/auth/protected` requires authentication and provides a minimal protected-resource check.
- `GET /api/admin/users` requires the `ADMIN` role and never returns password hashes.
- `POST /api/jobs` requires `ADMIN` or `RECRUITER`; created jobs are owned by the authenticated user.
- `GET /api/jobs/{job_id}` requires `ADMIN` or the owning `RECRUITER`; another recruiter's job returns `404` to avoid resource enumeration.
- `GET /api/jobs` lists all jobs for admins and only owned jobs for recruiters.
- `PATCH /api/jobs/{job_id}` updates title, department, or description for an authorized job. Invalid lifecycle transitions return `422`.
- `POST /api/jobs/{job_id}/requirements/analyze` returns validated draft requirements and does not persist them.
- `PUT /api/jobs/{job_id}/requirements` replaces finalized requirements for an authorized job and marks it `READY`.

Requirement analysis validates structured output before returning it; raw model output is never written to PostgreSQL. The V0.4 API adds job and requirement management. V0.5 adds:

- `POST /api/jobs/{job_id}/applications` for multipart candidate fields, required PDF/DOCX resume, and optional PDF/DOCX cover letter.
- `GET /api/jobs/{job_id}/applications` for authorized application summaries.
- `GET /api/applications/{application_id}` for authorized candidate/application and document metadata.
- `GET /api/applications/{application_id}/documents` and `/documents/{document_id}` for authorized extracted document content.
- `GET /api/applications/{application_id}/chunks` for authorized deterministic source chunks.

All application/document/chunk endpoints authorize through the parent job. Unsupported, malformed, oversized, duplicate, and empty-text uploads return safe `422` errors. Raw filesystem paths are not exposed.

Authentication failures return `401` with a generic message. Authenticated users lacking a required role receive `403`. The frontend is not a security boundary.

Future endpoints must validate request and response schemas, avoid leaking secrets, and keep security decisions on the backend.
