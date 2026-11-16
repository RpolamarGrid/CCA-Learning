#!/usr/bin/env bash
# Task 3.6 — CI review script.
#
# The -p flag is the single most important thing here: it runs Claude Code
# in non-interactive ("print") mode. Without it, a CI runner has no TTY to
# supply input to, and the job hangs indefinitely waiting for input that
# will never arrive.
set -euo pipefail

TARGET_FILE="${1:-src/api/v1/createOrder.handler.ts}"

echo "=== CI review of: $TARGET_FILE ==="
echo "(using -p for non-interactive mode, --output-format json for machine-parseable findings)"
echo

claude -p "Review $TARGET_FILE against this project's CLAUDE.md and .claude/rules/ conventions. List any issues found as a short JSON array of {file, issue, severity}." \
  --output-format json \
  > ci_review_output.json

echo "=== Structured findings written to ci_review_output.json ==="
cat ci_review_output.json
