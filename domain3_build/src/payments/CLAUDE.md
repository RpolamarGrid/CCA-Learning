# Payments directory standards (Task 3.1 — directory-level)

This file ONLY applies when Claude Code is working inside `src/payments/`.
It does NOT apply repo-wide — that's the key distinction from project-level
CLAUDE.md. A developer working in `src/auth/` never loads this file.

## Payments-specific rules
- All monetary amounts are integers in minor units (cents), never floats.
- Every refund path must check the $500 manager-approval threshold before
  calling the payment gateway.
- Log every state transition on a Payment object (created, authorized,
  captured, refunded) with the transaction ID.
