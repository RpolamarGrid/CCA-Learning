---
paths: ["**/*.test.ts"]
---

# Test conventions (Task 3.3 — path-specific rule)

Loads ONLY when editing a file matching `**/*.test.ts`, regardless of which
directory it's in. This is the fix for conventions needing to apply to test
files co-located with source across many directories — a directory-level
CLAUDE.md can't do this because it's tied to one physical location, and a
single root CLAUDE.md would load this even when nowhere near a test file,
wasting tokens.

## Rules
- Every test file must use the `describe`/`it` structure, not bare `test()`.
- Mock only external I/O (network, filesystem, DB) — never mock the unit
  under test itself.
- Each test must assert on behaviour, not implementation detail (no
  snapshot-testing internal state shape).
