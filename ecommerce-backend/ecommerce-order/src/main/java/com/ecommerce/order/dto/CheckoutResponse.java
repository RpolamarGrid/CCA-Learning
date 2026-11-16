package com.ecommerce.order.dto;

import com.ecommerce.order.entity.OrderStatus;

public record CheckoutResponse(Long orderId, OrderStatus status, String paymentRedirectUrl) {
}
