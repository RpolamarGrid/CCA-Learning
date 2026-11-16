---
paths: ["**/*.handler.ts"]
---

# API handler conventions (Task 3.3 — path-specific rule)

Loads ONLY when editing a file matching `**/*.handler.ts` — covers
`src/api/v1/`, `src/api/v2/`, `src/internal/api/`, and anywhere else a
handler file exists, without needing a directory-level CLAUDE.md duplicated
into every one of those locations.

## Rules
- Every handler must validate its input against a schema before touching
  business logic.
- Every handler returns a structured error shape on failure: `{isError,
  errorCategory, isRetryable, description}` (see Domain 2, Task 2.2).
- No handler may call another handler directly — route through the service
  layer.
