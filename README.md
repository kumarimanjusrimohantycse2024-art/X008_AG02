# TalentScreen

TalentScreen is an evidence-aware talent-acquisition screening foundation. This repository is **V0.1: Foundation only**. It establishes the frontend, backend, database boundary, startup flow, contracts, and checks that future screening features can build on.

## Architecture

- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Backend: FastAPI, Pydantic, Uvicorn
- Database: PostgreSQL with a pgvector-ready image
- Security: environment-driven, JWT-ready boundaries; authentication is not implemented in V0.1

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

Install dependencies:

```powershell
python -m pip install -r backend/requirements.txt
Push-Location frontend
npm install
Pop-Location
```

## PostgreSQL

Start the local database:

```powershell
docker compose up -d postgres
```

The backend reports database availability at `/api/health/database`; it does not fake a successful connection. This project publishes PostgreSQL on host port `5434` to avoid colliding with other local PostgreSQL services.

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

## Planned versions

- V0.2: domain models, requisitions, applications, and deterministic service boundaries
- V0.3: authentication, authorization, and resource ownership
- Later: document processing, claim extraction, terminology resolution, evidence verification, ranking, and pool-gap analysis

Candidate upload, parsing, embeddings, LLM screening, ranking, Redis, Kafka, Kubernetes, and production deployment are intentionally out of scope for V0.1.
