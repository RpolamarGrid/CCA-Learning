package com.ecommerce.order.event;

import java.util.List;

/**
 * Published after payment success + order persisted; consumed asynchronously
 * by the inventory module to decrement stock, decoupling checkout latency
 * from inventory-write latency (Observer/event-driven pattern).
 */
public record OrderConfirmedEvent(Long orderId, List<OrderLine> lines) {

    public record OrderLine(Long productId, int quantity) {
    }
}
