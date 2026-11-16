package com.ecommerce.order.entity;

import java.util.Map;
import java.util.Set;

/**
 * Order state machine. Each status declares the set of states it may legally
 * transition into; CREATED -> PAID -> INVENTORY_RESERVED -> CONFIRMED is the
 * happy path, with FAILED/COMPENSATED as terminal error branches.
 */
public enum OrderStatus {
    CREATED,
    PAID,
    INVENTORY_RESERVED,
    CONFIRMED,
    FAILED,
    COMPENSATED;

    private static final Map<OrderStatus, Set<OrderStatus>> ALLOWED_TRANSITIONS = Map.of(
            CREATED, Set.of(PAID, FAILED),
            PAID, Set.of(INVENTORY_RESERVED, FAILED),
            INVENTORY_RESERVED, Set.of(CONFIRMED, COMPENSATED),
            CONFIRMED, Set.of(COMPENSATED),
            FAILED, Set.of(),
            COMPENSATED, Set.of());

    public boolean canTransitionTo(OrderStatus next) {
        return ALLOWED_TRANSITIONS.getOrDefault(this, Set.of()).contains(next);
    }
}
