package com.ecommerce.payment.gateway;

import com.ecommerce.payment.dto.PaymentInitiationResult;
import com.ecommerce.payment.dto.PaymentVerificationResult;
import com.ecommerce.payment.dto.RefundResult;
import java.math.BigDecimal;

/**
 * Strategy/Adapter boundary for payment providers. Order/checkout code depends
 * only on this interface - never on a specific provider SDK - so swapping or
 * adding gateways (Razorpay, Stripe, ...) never touches order orchestration logic.
 * See .claude/rules/payment-gateway.md and docs/adr/0003-payment-gateway-adapter-pattern.md.
 */
public interface PaymentGateway {

    String gatewayName();

    PaymentInitiationResult initiate(String merchantOrderId, BigDecimal amount, String callbackUrl);

    PaymentVerificationResult verify(String providerTransactionId);

    RefundResult refund(String providerTransactionId, BigDecimal amount);
}
