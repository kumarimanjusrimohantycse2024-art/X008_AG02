# API Contract

V0.2 endpoints:

- `GET /` returns API identification and readiness.
- `GET /api/health` returns `{ status, service, version, database }`, preserving the V0.1 fields and adding real database status.
- `GET /api/health/database` reports a real PostgreSQL connectivity check as `connected` or `unavailable`.

The V0.2 data layer intentionally does not expose CRUD endpoints yet. SQLAlchemy models and Pydantic create/read/update contracts are prepared for later API versions.

Future endpoints must validate request and response schemas, avoid leaking secrets, and keep security decisions on the backend.
