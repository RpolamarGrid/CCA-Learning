# 0006: Scaling path to ~1M users

## Context
The current build is a single-instance modular monolith suitable for demonstrating the full
vertical slice. This ADR documents - as illustrative, not load-tested - how the architecture
extends toward ~1M users.

## Decision (future work, documented now)

- **Stateless app tier**: JWT auth (no server session) already allows horizontal scaling of
  `ecommerce-app` behind a load balancer with no sticky-session requirement (except the SSE
  admin stream, see ADR 0005).
- **Postgres**: add read replicas for catalog/product browsing (read-heavy, tolerant of
  replication lag); writes (orders, inventory, payments) stay on the primary. Longer-term,
  shard by customer/order id range if write volume on orders/inventory becomes the bottleneck.
- **Redis**: used for OTP, cart, rate limiting. At scale, size for session/cart working-set
  (illustrative: 1M carts x ~2KB average serialized size = ~2GB, plus OTP/rate-limit keys which
  are small and short-TTL) and consider Redis Cluster for horizontal capacity + HA.
- **Kafka migration path**: replace in-process `ApplicationEventPublisher` events with Kafka
  topics once multi-instance durability/ordering matters - e.g. `order.confirmed`,
  `inventory.shortfall`, `order.status-changed`. Partition `order.confirmed` by `productId` (or
  `orderId`) to preserve per-product ordering for inventory consumers; consumer group per
  module (inventory, notifications, SSE-fanout).
- **CDN**: product images/static assets served from a CDN, not the app tier.
- **Rate limiting**: already implemented for OTP send (Redis counter + TTL); at scale, apply the
  same pattern (or an API gateway-level limiter) to login and checkout endpoints to blunt abuse.
- **Idempotency**: payment webhook idempotency (unique constraint on `providerTransactionId`,
  see `ProcessedWebhookEvent`) remains essential at scale since providers routinely retry
  webhooks; this pattern extends unchanged.
- **Back-of-envelope capacity sketch (illustrative, not load-tested)**:
  - 1M monthly active users, assume ~5% concurrent peak => ~50K concurrent sessions.
  - Peak browse traffic ballpark: ~500 req/s on product listing/detail (cacheable, read-replica +
    CDN-fronted where possible).
  - Peak checkout traffic ballpark: ~20-50 req/s (checkout is a small fraction of browse traffic).
  - DB connection pool: with HikariCP, ~10-20 connections per app instance x 10-20 instances is
    already in Postgres's comfortable range (a few hundred connections) if using a connection
    pooler (PgBouncer) in front of Postgres for anything larger.
  - Redis: cart + OTP + rate-limit keyspace in low single-digit GB at 1M users; CPU-bound more
    than memory-bound at these volumes.
  - Kafka (if/when adopted): 6-12 partitions per core topic is a reasonable illustrative starting
    point for 1M-user scale, revisited based on actual consumer throughput measurements.
- **Multi-region**: explicitly out of scope / future work. Would require active-active or
  active-passive Postgres replication strategy, region-aware routing, and careful handling of
  payment-provider region constraints (PhonePe is India-specific, for example).

## Consequences
This ADR intentionally documents direction, not a committed implementation - none of the above
(Kafka, read replicas, CDN, multi-region) is built in this repository. Treat all numbers as
illustrative sizing exercises, not benchmarked guarantees.
