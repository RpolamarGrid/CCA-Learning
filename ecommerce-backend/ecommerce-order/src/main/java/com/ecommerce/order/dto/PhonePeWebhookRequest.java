package com.ecommerce.order.dto;

import jakarta.validation.constraints.NotBlank;

public record PhonePeWebhookRequest(
        @NotBlank String merchantTransactionId,
        @NotBlank String providerTransactionId,
        @NotBlank String status) {
}
