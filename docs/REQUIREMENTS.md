# V0.4 Requirements Workflow

V0.4 lets an authenticated recruiter create a job requisition, request a structured requirement draft, review and edit it, and save the finalized set. The server derives ownership from the authenticated user; `created_by` is never accepted from the client.

## Lifecycle

```text
DRAFT -> READY -> SCREENING -> COMPLETED
```

V0.4 permits `DRAFT -> READY` after a valid non-empty requirement set. Screening transitions are reserved for later versions. Admin access follows the V0.3 policy.

## Requirement schema

Each requirement contains `name`, `description`, `priority`, explicit `minimum_years` when stated, deterministic `weight`, conservative `aliases`, and `evidence_expectations` for future evidence metadata.

The backend rejects empty names/descriptions, negative experience values, non-positive weights, malformed fields, and duplicate normalized names.

## AI boundary

The extractor receives only job-description text. The description is untrusted data, not instructions to the model. Raw output is parsed and validated through Pydantic before it is returned. Analysis is a draft operation and does not write requirements. The development fallback is deterministic and controlled by `DEMO_MODE`; normal configuration fails safely when no provider is available.

V0.4 does not implement candidate creation, document ingestion, embeddings, evidence verification, scoring, ranking, or hiring decisions.

## Authorization

Every job and requirement operation resolves the job through the V0.3 ownership dependency. Recruiters can access only jobs where `jobs.created_by` equals their user ID. Admins retain established administrative access. Child-resource operations authorize their parent job first.

## Frontend pages

- `/jobs`: accessible job list and create action
- `/jobs/new`: job draft creation and requirement analysis
- `/jobs/[jobId]`: job detail and requirement counts
- `/jobs/[jobId]/requirements`: editable AI-suggested requirement review