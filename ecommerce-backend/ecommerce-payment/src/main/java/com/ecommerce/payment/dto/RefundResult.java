package com.ecommerce.payment.dto;

public record RefundResult(String providerRefundId, PaymentStatus status) {
}
