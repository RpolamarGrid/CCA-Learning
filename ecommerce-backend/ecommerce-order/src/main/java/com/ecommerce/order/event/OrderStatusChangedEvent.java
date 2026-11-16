package com.ecommerce.order.event;

import com.ecommerce.order.entity.OrderStatus;

/** Published on every order state transition; consumed by the admin SSE stream. */
public record OrderStatusChangedEvent(Long orderId, OrderStatus status) {
}
