# TalentScreen

TalentScreen is an evidence-aware talent-acquisition screening foundation. This repository is **V0.5: Application Ingestion & Source Processing**. V0.1 established the foundation, V0.2 added the persistent domain model, V0.3 added secure authentication/RBAC, V0.4 added job/requirement workflows, and V0.5 adds recruiter-owned application ingestion without implementing AI evidence intelligence.

## Architecture

- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Backend: FastAPI, Pydantic, Uvicorn
- Database: PostgreSQL with pgvector, SQLAlchemy 2.x, and Alembic
- Security: PBKDF2 password hashing, expiring JWT bearer tokens, ADMIN/RECRUITER roles, and server-side ownership checks
- Product workflow: recruiter-owned job drafts, validated requirement analysis, editable review, and READY lifecycle transition
- Application workflow: PDF/DOCX upload, deterministic parsing, source-aware chunks, and application ownership checks

## Prerequisites

- Python 3.11+
- Node.js 20+
- npm
- Docker Desktop for PostgreSQL

## Environment setup

Copy `.env.example` to `.env` and adjust values as needed. Never commit `.env` or real secrets.

```powershell
Copy-Item .env.example .env
```

Set a strong `JWT_SECRET` for non-development environments. `ACCESS_TOKEN_EXPIRE_MINUTES` defaults to 60. The frontend stores only the access token in `localStorage` for this local split-origin demo; this is a deliberate trade-off documented in [docs/SECURITY_RULES.md](docs/SECURITY_RULES.md), not a production recommendation.

Install dependencies:

```powershell
python -m pip install -r backend/requirements.txt
Push-Location frontend
npm install
Pop-Location
```

## PostgreSQL and migrations

Start the local database:

```powershell
docker compose up -d postgres
```

This project publishes PostgreSQL on host port `5434` to avoid colliding with other local PostgreSQL services. Apply the V0.2 schema with:

```powershell
python -m alembic upgrade head
```

The backend reports database availability at `/api/health/database`; it does not fake a successful connection. See [docs/DATABASE.md](docs/DATABASE.md) for entities, migrations, seeds, and test strategy.

## Development startup

Run both services with LAN-friendly bindings:

```powershell
python start.py
# Windows shortcut
start_talentscreen.bat
```

Demo mode is recognized but only sets the environment flag in V0.1:

```powershell
python start.py --demo
```

Seed minimal development records with an already-hashed value:

```powershell
$env:SEED_PASSWORD_HASH = "<already-hashed-development-value>"
python -m app.db.seed
```

For separate terminals:

```powershell
Push-Location backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Pop-Location
Push-Location frontend
npm run dev
Pop-Location
```

## URLs and health checks

- Local frontend: http://localhost:3000
- Network frontend: http://<LAN-IP>:3000
- Backend: http://localhost:8000
- API health: http://localhost:8000/api/health
- Database health: http://localhost:8000/api/health/database
- Login: http://localhost:3000/login
- Jobs: http://localhost:3000/jobs
- Application upload: http://localhost:3000/jobs/<job-id>/applications/new

The frontend status indicator calls the backend health endpoint and displays checking, connected, or unavailable. Configure a different backend with `NEXT_PUBLIC_BACKEND_URL` when needed.

## Project structure

```text
frontend/       Next.js App Router shell
backend/        FastAPI application, settings, database adapter, tests
database/       Migration and seed placeholders
scripts/        Developer utility placeholder
docs/           Architecture and stable project contracts
start.py        Cross-platform process launcher
start_talentscreen.bat  Windows launcher
docker-compose.yml       PostgreSQL + pgvector-ready development database
```

## Current and planned versions

- V0.2: persistent entities, UUIDs, constraints, relationships, migrations, seed infrastructure, and database tests
- V0.3: secure login, password hashing, expiring JWTs, role authorization, job ownership, and authenticated frontend state

- V0.3: authentication, authorization, and resource ownership
- V0.4: job creation, requirement extraction/review, finalized requirements, and job lifecycle
- V0.5: candidate/application ingestion, PDF/DOCX parsing, deterministic chunks, and source traceability
- Later: document processing, claim extraction, terminology resolution, evidence verification, ranking, and pool-gap analysis

Candidate upload, parsing, embeddings, LLM screening, ranking, Redis, Kafka, Kubernetes, and production deployment are intentionally out of scope for V0.1.
