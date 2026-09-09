# API Contract

V0.1 endpoints:

- `GET /` returns API identification and readiness.
- `GET /api/health` returns `{ status, service, version }`.
- `GET /api/health/database` reports a real PostgreSQL connectivity check as `connected` or `unavailable`.

Future endpoints must validate request and response schemas, avoid leaking secrets, and keep security decisions on the backend.
