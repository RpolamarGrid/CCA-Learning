package com.ecommerce.payment.gateway;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.ecommerce.common.exception.BusinessException;
import com.ecommerce.payment.dto.PaymentInitiationResult;
import com.ecommerce.payment.dto.PaymentStatus;
import com.ecommerce.payment.dto.PaymentVerificationResult;
import com.ecommerce.payment.dto.RefundResult;
import java.math.BigDecimal;
import java.util.List;
import org.junit.jupiter.api.Test;

class PaymentGatewayFactoryTest {

    private final PaymentGateway stubGateway = new PaymentGateway() {
        @Override
        public String gatewayName() {
            return "STUB";
        }

        @Override
        public PaymentInitiationResult initiate(String merchantOrderId, BigDecimal amount, String callbackUrl) {
            return new PaymentInitiationResult("txn", "url", PaymentStatus.SUCCESS);
        }

        @Override
        public PaymentVerificationResult verify(String providerTransactionId) {
            return new PaymentVerificationResult(providerTransactionId, PaymentStatus.SUCCESS, null);
        }

        @Override
        public RefundResult refund(String providerTransactionId, BigDecimal amount) {
            return new RefundResult("refund", PaymentStatus.SUCCESS);
        }
    };

    @Test
    void resolvesRegisteredGatewayByName() {
        PaymentGatewayFactory factory = new PaymentGatewayFactory(List.of(stubGateway));
        assertThat(factory.resolve("STUB")).isSameAs(stubGateway);
    }

    @Test
    void throwsForUnknownGateway() {
        PaymentGatewayFactory factory = new PaymentGatewayFactory(List.of(stubGateway));
        assertThatThrownBy(() -> factory.resolve("UNKNOWN")).isInstanceOf(BusinessException.class);
    }
}
