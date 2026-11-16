package com.ecommerce.order.web;

import com.ecommerce.common.dto.ApiResponse;
import com.ecommerce.order.dto.PhonePeWebhookRequest;
import com.ecommerce.order.service.PaymentWebhookService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/** Public (unauthenticated) endpoint - PhonePe calls this server-to-server. */
@RestController
@RequestMapping("/api/payments/phonepe")
public class PhonePeWebhookController {

    private final PaymentWebhookService paymentWebhookService;

    public PhonePeWebhookController(PaymentWebhookService paymentWebhookService) {
        this.paymentWebhookService = paymentWebhookService;
    }

    @PostMapping("/webhook")
    public ApiResponse<Void> webhook(@Valid @RequestBody PhonePeWebhookRequest request) {
        paymentWebhookService.handle(request);
        return ApiResponse.ok(null);
    }
}
