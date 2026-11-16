# Hooks (illustrative example only)

This project does not ship a full hook pipeline. One illustrative example is documented here to
show the intended pattern - a pre-commit-style hook that flags a new `PaymentGateway`
implementation that lacks a corresponding test file.

Example `settings.json` hook snippet (not wired into CI, illustrative only):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hook": "scripts/check-payment-gateway-test-coverage.sh"
      }
    ]
  }
}
```

`scripts/check-payment-gateway-test-coverage.sh` (not included) would, in concept:

1. Detect when a new file under `ecommerce-payment/.../gateway/*GatewayAdapter.java` is written.
2. Check whether a matching `*GatewayAdapterTest.java` exists under `src/test/java` in the same
   module.
3. Emit a warning (non-blocking) if the test file is missing, reminding the author to add
   coverage per `.claude/skills/add-payment-gateway/SKILL.md`.

This repo intentionally keeps the hook as documentation only, to avoid over-engineering tooling
that isn't exercised by the current build.
