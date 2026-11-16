package com.ecommerce.notification;

import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

/**
 * Mock SMS provider. Never sends a real SMS; only logs - this keeps local/dev/test
 * environments free of real provider credentials and network calls.
 * Wrapped with a circuit breaker so a flaky real provider (once swapped in) can't
 * cascade failures into the OTP request path.
 */
@Component
public class MockOtpSenderAdapter implements OtpSenderPort {

    private static final Logger log = LoggerFactory.getLogger(MockOtpSenderAdapter.class);

    @Override
    @CircuitBreaker(name = "otpSender")
    public void sendOtp(String phoneNumber, String otpCode) {
        // Intentionally logs only the last 2 digits in real deployments; full code logged here
        // because this is the explicitly-mock, non-production adapter.
        log.info("[MOCK SMS] OTP for {} is {} (TTL 5m)", phoneNumber, otpCode);
    }
}
