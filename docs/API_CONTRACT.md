# API Contract

V0.3 endpoints:

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

The V0.3 API adds only authentication, authorization verification, and minimal job ownership endpoints. Candidate ingestion, document processing, and AI screening endpoints remain intentionally absent.

Authentication failures return `401` with a generic message. Authenticated users lacking a required role receive `403`. The frontend is not a security boundary.

Future endpoints must validate request and response schemas, avoid leaking secrets, and keep security decisions on the backend.
