# Project-wide standards (Task 3.1 — project-level)

This file is version-controlled and shared with every developer on this repo.
Applies everywhere in the codebase, every session, automatically.

## Universal conventions
- Use TypeScript strict mode in all new files.
- API responses use camelCase keys, never snake_case.
- Every exported function must have a docstring explaining WHY, not WHAT.
- Error handling: never swallow exceptions silently — log or propagate.

## Modular organisation (Task 3.1)
Topic-specific rules live in `.claude/rules/` rather than being crammed into
this single file — see `test-conventions.md` and `api-conventions.md` for
path-scoped rules that only load when relevant files are being edited.
