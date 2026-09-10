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

## V0.7 candidate assessment

Candidate assessment consumes persisted V0.6 requirement assessments only. It does not reread documents, re-extract claims, or ask a model to reassess evidence. Required and preferred coverage are counted separately across `MET`, `PARTIALLY_MET`, `UNSUPPORTED`, and `NOT_FOUND`; evidence quality is counted separately across `STRONG`, `MODERATE`, `WEAK`, and `NONE`.

The recommendation policy is deterministic: `STRONG_MATCH` requires every required requirement to be `MET` with no missing required item and strong or moderate aggregate evidence; `GOOD_MATCH` requires at least 80% weighted required coverage, allowing partial requirements, with strong or moderate evidence; `MIXED_MATCH` requires meaningful required coverage but material gaps; otherwise the result is `WEAK_MATCH`. Preferred requirements never compensate for required gaps.

Strengths, weaknesses, and trade-offs reference only verified assessment and source IDs from the same application. V0.7 does not rank candidates, generate shortlists, compare candidates, or perform pool-gap analysis. No LLM is required for the deterministic explanation layer; any future wording model must receive structured verified assessments only and pass the same policy validator.
