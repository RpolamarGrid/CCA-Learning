package com.ecommerce.payment.gateway;

import com.ecommerce.common.exception.BusinessException;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.springframework.stereotype.Component;

/**
 * Factory pattern: resolves a {@link PaymentGateway} implementation by name
 * so callers (CheckoutService) never new-up or hardcode a concrete adapter.
 * Adding a gateway = implement the interface, register as a Spring bean;
 * the factory picks it up automatically.
 */
@Component
public class PaymentGatewayFactory {

    private final Map<String, PaymentGateway> gatewaysByName;

    public PaymentGatewayFactory(List<PaymentGateway> gateways) {
        this.gatewaysByName = gateways.stream()
                .collect(Collectors.toMap(PaymentGateway::gatewayName, Function.identity()));
    }

    public PaymentGateway resolve(String gatewayName) {
        PaymentGateway gateway = gatewaysByName.get(gatewayName);
        if (gateway == null) {
            throw new BusinessException("UNKNOWN_PAYMENT_GATEWAY", "No payment gateway registered for: " + gatewayName);
        }
        return gateway;
    }
}
