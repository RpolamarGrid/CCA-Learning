# Rule: Payment gateway abstraction must never leak

- Every payment provider integration MUST implement `com.ecommerce.payment.gateway.PaymentGateway`
  and be registered as a Spring bean so `PaymentGatewayFactory` can resolve it by `gatewayName()`.
- `CheckoutService`, `OrderService`, and any other order-orchestration code MUST depend only on
  `PaymentGateway` / `PaymentGatewayFactory` - never import or call a concrete provider SDK
  (e.g. a PhonePe client class) directly.
- New gateways are added via the `.claude/skills/add-payment-gateway` skill.
- Do not hardcode merchant IDs, salt keys, or API secrets in adapter code; read them from
  `@Value` properties backed by environment variables.
