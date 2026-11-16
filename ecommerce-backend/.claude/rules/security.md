# Rule: Security invariants

- All admin mutation endpoints (anything under `/api/admin/**` or that creates/updates/deletes
  state as an admin) MUST be annotated with `@PreAuthorize("hasRole('ADMIN')")` at the controller
  or method level - never rely on URL pattern matching alone.
- OTP codes MUST only ever live in Redis with a TTL (currently 5 minutes). Never log a full OTP
  code outside the explicitly-mock `MockOtpSenderAdapter`, and never persist an OTP code to the
  relational database or any durable store.
- All request DTOs MUST use Bean Validation (`@Valid` + constraint annotations) at the controller
  boundary.
- CSRF is disabled only because this API is stateless and JWT-bearer-token only; if any endpoint
  ever becomes session/cookie-based, CSRF protection must be re-enabled for it.
