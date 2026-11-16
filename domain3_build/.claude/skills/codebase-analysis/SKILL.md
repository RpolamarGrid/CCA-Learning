---
name: codebase-analysis
description: Produces a verbose structural analysis of a directory (file counts, exported symbols, dependency hints) without cluttering the main conversation.
context: fork
allowed-tools: ["Read", "Grep", "Glob"]
argument-hint: "<directory-path>"
---

# Codebase Analysis Skill (Task 3.2)

This skill demonstrates all three frontmatter options taught in 3.2:

- `context: fork` — runs in an isolated sub-agent context. The noisy,
  exploratory output (every file it reads, every grep match) stays
  contained in the fork; only a final summary returns to the main
  conversation.
- `allowed-tools: ["Read", "Grep", "Glob"]` — restricted to read-only
  tools. This skill cannot Write or Edit anything, even accidentally,
  because those tools simply aren't available to it during execution.
- `argument-hint: "<directory-path>"` — if invoked bare (no argument),
  the developer is prompted for which directory to analyse.

## Instructions

Given a directory path as input:

1. Use Glob to list all files under that directory.
2. Use Grep to find all `export` statements across those files.
3. Use Read on each file only as needed to understand exported symbols.
4. Produce a structured summary: file count, exported symbol count per
   file, and any files with no exports (dead code candidates).

Return ONLY the final summary — do not narrate every intermediate search
step, since that output is exactly what `context: fork` is isolating away
from the main conversation.
