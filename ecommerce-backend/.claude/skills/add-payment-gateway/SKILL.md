# Skill: Add a new payment gateway

1. Create a new class in `ecommerce-payment/src/main/java/com/ecommerce/payment/gateway/`
   implementing `PaymentGateway` (`gatewayName()`, `initiate()`, `verify()`, `refund()`).
2. Annotate it `@Component` so Spring registers it; `PaymentGatewayFactory` picks it up
   automatically via constructor injection of `List<PaymentGateway>`.
3. Wrap outbound HTTP calls with `@CircuitBreaker` (Resilience4j), matching the pattern used in
   `PhonePeGatewayAdapter`, and add a named instance under `resilience4j.circuitbreaker.instances`
   in `application.yml`.
4. Read all provider credentials via `@Value` properties backed by environment variables; add
   corresponding placeholders to `.env.example` (never real secrets).
5. Add unit tests for the new adapter (checksum/signature generation, success/failure mapping)
   and a `PaymentGatewayFactoryTest`-style test confirming the new gateway resolves by name.
6. Do not modify `CheckoutService`/`OrderService` to call the new adapter directly - resolve it
   via `PaymentGatewayFactory.resolve(gatewayName)` and set `app.payment.default-gateway` (or a
   per-order override) to switch providers.
