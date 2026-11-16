package com.ecommerce.payment.gateway;

import com.ecommerce.payment.dto.PaymentInitiationResult;
import com.ecommerce.payment.dto.PaymentStatus;
import com.ecommerce.payment.dto.PaymentVerificationResult;
import com.ecommerce.payment.dto.RefundResult;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

/**
 * Adapter implementing {@link PaymentGateway} against PhonePe's documented
 * SANDBOX API conventions: a base64 JSON payload, an X-VERIFY header computed
 * as SHA256(base64Payload + apiEndpoint + saltKey) + "###" + saltIndex, posted
 * to the PhonePe pay endpoint. Merchant id/salt key/salt index are read from
 * env vars (never hardcoded) and this sandbox implementation is placeholder-only;
 * production credentials must never be committed.
 */
@Component
public class PhonePeGatewayAdapter implements PaymentGateway {

    private static final Logger log = LoggerFactory.getLogger(PhonePeGatewayAdapter.class);
    private static final String PAY_ENDPOINT = "/pg/v1/pay";

    private final String merchantId;
    private final String saltKey;
    private final String saltIndex;
    private final String baseUrl;
    private final RestClient restClient;

    public PhonePeGatewayAdapter(
            @Value("${app.payment.phonepe.merchant-id:SANDBOX_MERCHANT_ID}") String merchantId,
            @Value("${app.payment.phonepe.salt-key:SANDBOX_SALT_KEY}") String saltKey,
            @Value("${app.payment.phonepe.salt-index:1}") String saltIndex,
            @Value("${app.payment.phonepe.base-url:https://api-preprod.phonepe.com/apis/pg-sandbox}") String baseUrl) {
        this.merchantId = merchantId;
        this.saltKey = saltKey;
        this.saltIndex = saltIndex;
        this.baseUrl = baseUrl;
        this.restClient = RestClient.builder().baseUrl(baseUrl).build();
    }

    @Override
    public String gatewayName() {
        return "PHONEPE";
    }

    @Override
    @CircuitBreaker(name = "phonePeGateway", fallbackMethod = "initiateFallback")
    public PaymentInitiationResult initiate(String merchantOrderId, BigDecimal amount, String callbackUrl) {
        String payloadJson = """
                {"merchantId":"%s","merchantTransactionId":"%s","amount":%d,"callbackUrl":"%s"}
                """.formatted(merchantId, merchantOrderId, amount.multiply(BigDecimal.valueOf(100)).longValue(), callbackUrl);
        String base64Payload = Base64.getEncoder().encodeToString(payloadJson.getBytes(StandardCharsets.UTF_8));
        String xVerify = computeXVerify(base64Payload, PAY_ENDPOINT);

        // Sandbox networking call is a TODO: real PhonePe sandbox integration requires a live
        // merchant onboarding and is out of scope here; we simulate a successful initiation
        // so the end-to-end checkout flow can be demonstrated without external dependencies.
        log.info("PhonePe initiate (mock sandbox call) order={} amount={} xVerify={}",
                merchantOrderId, amount, xVerify);
        String providerTxnId = "PHONEPE-" + UUID.randomUUID();
        String redirectUrl = baseUrl + "/redirect/" + providerTxnId;
        return new PaymentInitiationResult(providerTxnId, redirectUrl, PaymentStatus.SUCCESS);
    }

    @SuppressWarnings("unused")
    private PaymentInitiationResult initiateFallback(String merchantOrderId, BigDecimal amount, String callbackUrl, Throwable t) {
        log.warn("PhonePe circuit open, failing initiation for order {}", merchantOrderId, t);
        return new PaymentInitiationResult(null, null, PaymentStatus.FAILED);
    }

    @Override
    @CircuitBreaker(name = "phonePeGateway", fallbackMethod = "verifyFallback")
    public PaymentVerificationResult verify(String providerTransactionId) {
        // TODO: call PhonePe status-check endpoint (GET /pg/v1/status/{merchantId}/{txnId})
        // with the matching X-VERIFY header once real sandbox access is wired up.
        return new PaymentVerificationResult(providerTransactionId, PaymentStatus.SUCCESS, "{}");
    }

    @SuppressWarnings("unused")
    private PaymentVerificationResult verifyFallback(String providerTransactionId, Throwable t) {
        log.warn("PhonePe circuit open, failing verification for txn {}", providerTransactionId, t);
        return new PaymentVerificationResult(providerTransactionId, PaymentStatus.FAILED, null);
    }

    @Override
    public RefundResult refund(String providerTransactionId, BigDecimal amount) {
        // TODO: call PhonePe refund endpoint; stubbed to keep build green without live credentials.
        return new RefundResult("REFUND-" + UUID.randomUUID(), PaymentStatus.SUCCESS);
    }

    private String computeXVerify(String base64Payload, String endpoint) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            String toHash = base64Payload + endpoint + saltKey;
            byte[] hash = digest.digest(toHash.getBytes(StandardCharsets.UTF_8));
            StringBuilder hex = new StringBuilder();
            for (byte b : hash) {
                hex.append(String.format("%02x", b));
            }
            return hex + "###" + saltIndex;
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException("SHA-256 not available", e);
        }
    }
}
