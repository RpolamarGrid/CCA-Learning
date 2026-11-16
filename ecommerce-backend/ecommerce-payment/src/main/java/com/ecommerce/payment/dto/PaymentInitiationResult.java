package com.ecommerce.payment.dto;

public record PaymentInitiationResult(String providerTransactionId, String redirectUrl, PaymentStatus status) {
}
