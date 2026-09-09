# Security Rules

Future implementation requirements:

- Hash passwords; never store plaintext passwords.
- Use JWT-based authentication with safe secret configuration.
- Enforce authorization server-side.
- Check resource ownership on every protected resource.
- Validate file uploads by type, size, and content.
- Resist prompt injection and treat candidate text as untrusted.
- Isolate evidence at the application boundary.
- Never commit secrets, API keys, tokens, or passwords.

Authentication and full RBAC are intentionally not implemented in V0.1.
