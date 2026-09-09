# Architecture

TalentScreen V0.4 keeps the runtime small and explicit:

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

The frontend owns presentation and calls the API. FastAPI owns validation, security boundaries, and deterministic calculations. Services own domain workflows such as requirement extraction. SQLAlchemy provides the persistent data boundary, and job/child-resource access is authorized through `jobs.created_by`.

## V0.4 requisition workflow

```text
Recruiter -> Job draft -> Requirement extractor -> Pydantic validation
                                         -> Recruiter review/edit -> Final requirements -> Job READY
```

The extractor handles job requirements only. It does not read candidate documents, assess claims, rank candidates, or make hiring decisions.

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
