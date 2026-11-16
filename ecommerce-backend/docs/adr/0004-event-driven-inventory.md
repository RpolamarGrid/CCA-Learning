# 0004: Event-driven async inventory decrement

## Context
Decrementing inventory synchronously inside the checkout request would couple checkout latency
to inventory-table write latency/lock contention, and would force the checkout transaction to
span two concerns (payment confirmation + stock management) that can tolerate different
consistency windows (a few-hundred-ms lag on stock numbers is acceptable; a stuck payment
confirmation is not).

## Decision
`CheckoutService` publishes an `OrderConfirmedEvent` (Spring `ApplicationEventPublisher`) once the
order reaches `CONFIRMED`. `InventoryService.onOrderConfirmed` is an `@EventListener` marked
`@Async`, running on a separate thread pool, decrementing `Inventory.quantityAvailable`
transactionally per line item. `Inventory` uses `@Version` (optimistic locking, inherited from
`BaseEntity`) so concurrent decrements for the same product fail fast on conflict rather than
silently losing an update. If requested quantity exceeds available stock, an
`InventoryShortfallEvent` is published instead of decrementing.

## Consequences
- Checkout response returns as soon as payment + order persistence succeed; inventory lag is
  bounded by the async executor's queue, not by checkout request latency.
- A crash between order confirmation and inventory decrement is possible in this in-process event
  model (no durable outbox yet) - acceptable for this scope; see ADR 0006 for the Kafka-based
  durable-event migration path at scale.
- Optimistic-lock conflicts on `Inventory` currently surface as exceptions out of the async
  listener (logged, not retried) - a production hardening step would add retry-with-backoff or a
  dedicated outbox/queue consumer.
