# V0.5 Application Ingestion

V0.5 prepares traceable source material for V0.6. An authenticated recruiter uploads a required resume and optional cover letter to an authorized job. Candidate identity is entered explicitly; no AI extracts it.

## Supported files

Only parseable PDF and DOCX files are accepted. The backend checks extension, declared MIME type, PDF signature/parser validity, or DOCX ZIP structure. Files are limited by `MAX_UPLOAD_SIZE_MB` (10 MB by default). Image-only PDFs fail clearly because OCR is out of scope.

## Storage and metadata

Binary files are stored outside PostgreSQL:

```text
storage/uploads/{application_id}/{generated-uuid}.pdf
storage/uploads/{application_id}/{generated-uuid}.docx
```

Original names are metadata only. Each document stores file size, SHA-256, MIME type, extracted raw text, and document type. Uploads are ignored by Git.

## Parsing and chunking

PDF text is extracted page by page with `pypdf`, preserving source page numbers. DOCX paragraphs are read in document order with `python-docx`; reliable heading styles and known headings become section metadata, while page numbers remain null. Text normalization changes whitespace only and does not summarize or paraphrase.

Chunks are deterministic, target about 650 words with a 75-word overlap, and preserve `document_id`, `chunk_index`, `section`, and `page_number`. Embeddings are intentionally not generated and remain null.

## Failure behavior

The application is marked `PROCESSING`, then `COMPLETED` only after every document parses and chunks successfully. Malformed, unsupported, oversized, duplicate, or empty-text uploads mark ingestion `FAILED`, remove partial document rows/files, and return a safe validation message.

## Scope boundary

V0.5 ingestion does not implement LLM calls, OCR, embeddings, claims, evidence verification, ranking, scoring, semantic search, or pool-gap analysis. V0.6 adds application-scoped claim extraction, terminology resolution, mock embedding generation, and source-linked evidence analysis on top of this stored source material. Ranking, recommendations, and pool-gap analysis remain out of scope.