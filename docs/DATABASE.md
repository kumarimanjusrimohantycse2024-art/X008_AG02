# Database Foundation

V0.2 uses PostgreSQL, SQLAlchemy 2.x, Alembic, and the `pgvector/pgvector:pg16` image. The Compose service is published on host port `5434` because port `5432` is used by another local PostgreSQL service.

## Entity model

```text
User -> Jobs -> Requirements
             -> Applications -> Candidates
                              -> Documents -> Document chunks -> optional embeddings
                              -> Claims -> claim/requirement links
                              -> Evidence -> source chunks
                              -> Assessments -> candidate assessment
Jobs -> candidate rankings
Jobs + Requirements -> pool gaps
```

All application entities use UUID primary keys and timezone-aware lifecycle timestamps. Jobs retain `created_by` so V0.3 authorization can enforce ownership through the job/application chain.

Evidence keeps `application_id`, `claim_id`, `requirement_id`, and mandatory `source_chunk_id` explicitly. Similarity is stored separately from evidence strength and does not prove a skill.

## Migrations

Alembic is configured at the repository root:

```powershell
python -m alembic upgrade head
python -m alembic downgrade -1
python -m alembic upgrade head
```

The initial V0.2 migration creates the 14 domain tables, controlled PostgreSQL enums, foreign keys, indexes, constraints, the `vector` extension, and a nullable 1536-dimensional embedding column. The dimension is configured through `EMBEDDING_DIMENSION` and must match the migration/model when changed in a future migration.

## PostgreSQL setup

```powershell
docker compose up -d postgres
docker compose ps
```

Connection configuration defaults to:

```text
postgresql+psycopg://talentscreen:talentscreen@localhost:5434/talentscreen
```

The backend database health check is available at `/api/health/database` and reports `connected` only after `SELECT 1` succeeds.

## Seed data

The seed command creates one development user, one sample job, and two requirements. It accepts an externally supplied password hash for the legacy seed user, or hashes optional raw demo password environment values immediately:

```powershell
$env:SEED_PASSWORD_HASH = "<already-hashed-development-value>"
python -m app.db.seed
```

Optional V0.3 demo users use `DEMO_ADMIN_EMAIL`, `DEMO_ADMIN_PASSWORD`, `DEMO_RECRUITER_EMAIL`, and `DEMO_RECRUITER_PASSWORD`. Never commit those values. Seed values are idempotent for the configured emails/job.

## Tests

Database tests use PostgreSQL and wrap each test in a transaction that is rolled back afterward. They cover UUIDs, relationships, source-chunk traceability, constraints, Pydantic range validation, and application cascades:

```powershell
$env:PYTHONPATH = "backend"
python -m pytest backend/tests -q
```

No production or developer data should be used as a test database. For isolated CI, provide a separate `DATABASE_URL` pointing to a disposable PostgreSQL instance.
