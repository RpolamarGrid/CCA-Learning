# 0002: OTP-based customer authentication

## Context
Customers are identified by phone number, not a chosen username/password. We want low-friction
signup (no password to remember) and a mechanism resistant to credential stuffing. Admins, by
contrast, are a small trusted set and are fine with classic username/password.

## Decision
Customer auth is phone number + 6-digit OTP. The flow:
1. `POST /api/auth/customer/otp/send` with a phone number - rate-limited (max 3 sends/minute per
   number) - generates a 6-digit code and stores it in Redis with a 5-minute TTL, then calls
   `OtpSenderPort` (a mock adapter that only logs, in this build) to "deliver" it.
2. `POST /api/auth/customer/otp/verify` with phone number + code - checks Redis, and on match
   issues JWT access + refresh tokens (`ROLE_CUSTOMER`), creating a `CustomerUser` row lazily on
   first successful login.

OTP codes live only in Redis (never the relational DB) specifically so they expire automatically
and are never present in a backup/replica/audit log of the primary database.

## Consequences
- No password storage/reset flow needed for customers; simpler UX, smaller attack surface for
  credential leaks.
- Requires Redis to be available for login to work at all - Redis becomes a hard dependency for
  the customer auth path (acceptable, since it is already a hard dependency for cart).
- Rate limiting on send is essential to avoid OTP-spam/SMS-cost abuse; implemented via a Redis
  counter with TTL per phone number.
- Real SMS delivery is out of scope for this build; `OtpSenderPort` is the swap point for a real
  provider (Twilio, MSG91, etc.) without touching `OtpService` or the auth controllers.
