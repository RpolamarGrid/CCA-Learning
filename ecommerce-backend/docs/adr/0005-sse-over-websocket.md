# 0005: Server-Sent Events over WebSocket for admin order stream

## Context
The admin dashboard needs live order-status updates (`GET /admin/stream/orders`). The channel is
strictly server -> client (admin never needs to push data back over this connection).

## Decision
Use SSE (`SseEmitter`, `text/event-stream`) instead of WebSocket.

## Consequences
- Simpler implementation: plain HTTP, no upgrade handshake, works through standard reverse
  proxies/load balancers without special configuration.
- Automatic reconnect is built into the `EventSource` browser API, reducing client-side
  complexity compared to hand-rolled WebSocket reconnect logic.
- One-directional by design - if a future requirement needs admin -> server real-time messages
  over the same channel (not just normal REST calls), WebSocket would need to be reconsidered.
- At scale, each open SSE connection holds a server-side thread/emitter; horizontal scaling of the
  admin stream endpoint would need sticky routing or a pub/sub fan-out (e.g. Redis pub/sub or
  Kafka topic consumed per instance) rather than the current in-memory `CopyOnWriteArrayList` of
  emitters, which only works correctly on a single instance.
