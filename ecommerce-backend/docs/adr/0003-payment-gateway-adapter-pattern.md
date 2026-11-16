# 0003: Payment gateway via Strategy/Adapter + Factory

## Context
PhonePe is today's payment provider, but payment providers change over time (region expansion,
pricing negotiations, provider outages). Order/checkout logic must not be rewritten every time
the provider changes, and we must be able to add a second/alternate provider without touching
existing, tested checkout code.

## Decision
Define `PaymentGateway` (Strategy interface: `initiate`/`verify`/`refund`) in `ecommerce-payment`.
`PhonePeGatewayAdapter` implements it against PhonePe's documented sandbox conventions (base64
JSON payload + `X-VERIFY` checksum = `SHA256(payload + endpoint + saltKey) + "###" + saltIndex`).
`PaymentGatewayFactory` resolves a `PaymentGateway` bean by `gatewayName()` so callers never
instantiate a concrete adapter. `CheckoutService` depends only on `PaymentGatewayFactory`.

## Consequences
- Adding a new provider = new adapter class + Spring bean registration; zero changes to
  `CheckoutService`/`OrderService` (enforced by `.claude/rules/payment-gateway.md`).
- Outbound calls to PhonePe are wrapped in a Resilience4j `@CircuitBreaker` so a provider outage
  degrades gracefully (fails fast, returns `PaymentStatus.FAILED`) instead of hanging checkout
  requests.
- This build's PhonePe adapter mocks the actual network call (no live sandbox credentials
  available) while implementing the real checksum/signature logic, so swapping in genuine
  sandbox credentials only requires replacing the TODO-marked HTTP call bodies.
