# AI Contracts

V0.4 AI scope is limited to extracting structured requirements from an untrusted job description. The job description is data, not instructions to the model. Extracted requirements are drafts until a recruiter reviews and saves them.

The extractor distinguishes `REQUIRED` from `PREFERRED`, preserves explicit minimum experience, uses conservative aliases, and returns evidence expectations as future metadata only. It never evaluates candidates or fabricates requirements when unavailable.

Future evidence strength values:

- `strong`
- `moderate`
- `weak`
- `none`

Future assessment status values:

- `met`
- `partially_met`
- `unsupported`
- `not_found`

All future AI outputs must be schema validated. Similarity is a retrieval signal, not proof. The backend remains responsible for deterministic policy and evidence isolation.
