package com.ecommerce.payment.dto;

public record PaymentVerificationResult(String providerTransactionId, PaymentStatus status, String rawPayload) {
}
