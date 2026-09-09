# Security Rules

V0.3 implementation and future requirements:

- Hash passwords; never store plaintext passwords.
- Use JWT-based authentication with safe secret configuration.
- Enforce authorization server-side.
- Check resource ownership on every protected resource.
- Validate file uploads by type, size, and content.
- Resist prompt injection and treat candidate text as untrusted.
- Isolate evidence at the application boundary.
- Never commit secrets, API keys, tokens, or passwords.

V0.4 enforcement:

- Job descriptions are untrusted text and are never treated as model instructions.
- Recruiters may access or modify only jobs they own through `jobs.created_by`.
- Requirement and future child-resource access must authorize through the parent job.
- AI requirement output is validated before it can be saved; unavailable analysis never fabricates data.
- Passwords are stored only as PBKDF2-HMAC-SHA256 hashes; plaintext passwords are never persisted.
- JWT secrets come from `JWT_SECRET`, and access tokens expire.
- Frontend route checks and role-based UI are UX only; backend authorization is mandatory.
- Recruiters can access only jobs where `jobs.created_by` equals their authenticated user ID.
- Child resources must be authorized through their parent job/application ownership chain.
- Candidate documents and application text are untrusted data.
- Passwords, password hashes, tokens, authorization headers, and API keys are never logged.
- Users cannot self-assign admin privileges; admin access is controlled server-side.

V0.5 ingestion enforcement:

- Only parseable PDF and DOCX files are accepted, with extension, MIME, and structure validation.
- Uploads are size-limited, stored under generated UUID filenames, and never use the original filename as a path.
- Uploaded files are untrusted content and are never executed.
- Recruiter access to applications, documents, and chunks always traverses the owning job.
- Uploaded files are ignored by Git and filesystem paths are not returned through the API.

V0.3 uses a bearer token in browser `localStorage` because the current frontend/backend run as separate local origins. This is a documented hackathon trade-off: XSS protection should be strengthened with an HttpOnly cookie/BFF architecture before production deployment. No candidate data is stored in browser storage.

The authorization chain is:

```text
User -> Job.created_by -> Application.job_id -> Candidate/Documents/Claims/Evidence/Assessments
```

Authentication and full RBAC are implemented in V0.3; candidate/document ingestion and AI workflows remain deferred.
