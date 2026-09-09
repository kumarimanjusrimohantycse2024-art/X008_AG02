# Architecture

TalentScreen V0.1 keeps the runtime small and explicit:

```text
Next.js frontend
      |
      v
FastAPI API
      |
      v
Services and deterministic application logic
      |
      v
PostgreSQL (pgvector-ready)
```

The frontend owns presentation and calls the API. FastAPI owns validation, security boundaries, and deterministic calculations. Services are the future home for domain workflows. SQLAlchemy provides the database boundary without committing to the complete domain schema yet.

## Future evidence-aware pipeline

```text
Job Requisition
      -> Requirement Parser
      -> Applications
      -> Claim Extraction
      -> Terminology Resolution
      -> Evidence Retrieval
      -> Claim Verification
      -> Candidate Assessment
      -> Ranking
      -> Pool Gap Detection
```

V0.1 creates no pipeline implementation, document processor, embedding service, vector search, or candidate ranking behavior.
