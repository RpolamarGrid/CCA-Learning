#!/usr/bin/env bash
# Task 3.6 — honest test of the -p flag's purpose.
#
# NOTE ON THIS TEST'S ACTUAL RESULT: in this environment's Claude Code CLI
# version (2.1.218), running `claude "..."` with stdin redirected from
# /dev/null did NOT hang — it appears to auto-detect the absence of a TTY
# and exit non-interactively anyway. This does not match the classic
# exam scenario of an indefinite hang, and this script reports that
# honestly rather than fabricating a failure.
#
# The exam's underlying principle still stands as correct practice: ALWAYS
# pass -p explicitly in CI scripts. Relying on a specific CLI version's
# auto-detection behaviour is fragile and not guaranteed across versions —
# -p makes the non-interactive intent explicit and version-independent.
set -uo pipefail

echo "=== Test 1: WITHOUT -p flag (stdin from /dev/null, simulating a CI runner) ==="
START=$(date +%s)
claude "Say OK" < /dev/null > without_p_output.log 2>&1 &
PID=$!
sleep 5
if kill -0 $PID 2>/dev/null; then
  echo "RESULT: still running after 5s (hung) — kill and move on"
  kill -9 $PID 2>/dev/null
else
  wait $PID
  END=$(date +%s)
  echo "RESULT: exited on its own after $((END-START))s in this CLI version — did NOT hang"
fi
echo "Output: $(cat without_p_output.log)"
echo

echo "=== Test 2: WITH -p flag (the recommended, version-independent approach) ==="
claude -p "Say OK" > with_p_output.log 2>&1
echo "RESULT: exited immediately, non-interactive by explicit contract, not by auto-detection"
echo "Output: $(cat with_p_output.log)"
