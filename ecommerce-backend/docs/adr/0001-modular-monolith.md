# 0001: Modular monolith over microservices

## Context
We need to ship a full e-commerce vertical slice (catalog, cart, identity, payment, order,
inventory) quickly, with a small team and no existing operational platform (service mesh, shared
message bus, distributed tracing). Microservices-per-domain would multiply deployment, network,
and consistency complexity before any of it is needed.

## Decision
Build a single deployable Spring Boot application (`ecommerce-app`) composed of clearly bounded
Maven modules (`ecommerce-catalog`, `ecommerce-cart`, `ecommerce-identity`, `ecommerce-payment`,
`ecommerce-order`, `ecommerce-inventory`, `ecommerce-notification`, `ecommerce-common`). Modules
communicate in-process via well-defined interfaces (services, `ApplicationEventPublisher`), not
HTTP. Maven module boundaries enforce compile-time dependency direction (e.g. `ecommerce-order`
depends on `ecommerce-payment`'s interface, not vice versa).

## Consequences
- Simple deployment (one JAR/image), simple transaction management (JPA `@Transactional` works
  across what would otherwise be service boundaries), simple local dev (one `docker-compose up`).
- Module boundaries are a deliberate seam: if a module (e.g. inventory, or payment) later needs
  independent scaling or release cadence, its narrow interface (`PaymentGateway`,
  `OrderConfirmedEvent`) is the natural extraction point into its own service.
- Until then, all modules share one JVM's resource limits and one deployment lifecycle - a bug in
  one module can affect overall app availability. Mitigated by circuit breakers around genuinely
  external calls (PhonePe, SMS) and async event handling for inventory decrement.
