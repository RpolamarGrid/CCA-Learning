package com.ecommerce.identity.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;

import com.ecommerce.notification.OtpSenderPort;
import java.time.Duration;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.ValueOperations;

@ExtendWith(MockitoExtension.class)
class OtpServiceTest {

    @Mock
    private StringRedisTemplate redisTemplate;

    @Mock
    private ValueOperations<String, String> valueOperations;

    @Mock
    private OtpSenderPort otpSenderPort;

    @Test
    void sendOtpGeneratesSixDigitCodeWithTtlAndSendsViaPort() {
        when(redisTemplate.opsForValue()).thenReturn(valueOperations);
        when(redisTemplate.opsForValue().increment(anyString())).thenReturn(1L);

        OtpService otpService = new OtpService(redisTemplate, otpSenderPort);
        otpService.sendOtp("+15551234567");

        ArgumentCaptor<String> codeCaptor = ArgumentCaptor.forClass(String.class);
        org.mockito.Mockito.verify(valueOperations).set(eq("otp:code:+15551234567"), codeCaptor.capture(), eq(Duration.ofMinutes(5)));
        org.mockito.Mockito.verify(otpSenderPort).sendOtp(eq("+15551234567"), eq(codeCaptor.getValue()));
        assertThat(codeCaptor.getValue()).matches("\\d{6}");
    }

    @Test
    void verifyOtpReturnsTrueForMatchingCodeAndDeletesIt() {
        when(redisTemplate.opsForValue()).thenReturn(valueOperations);
        when(valueOperations.get("otp:code:+15551234567")).thenReturn("123456");

        OtpService otpService = new OtpService(redisTemplate, otpSenderPort);
        boolean result = otpService.verifyOtp("+15551234567", "123456");

        assertThat(result).isTrue();
        org.mockito.Mockito.verify(redisTemplate).delete("otp:code:+15551234567");
    }

    @Test
    void verifyOtpReturnsFalseForExpiredOrMissingCode() {
        when(redisTemplate.opsForValue()).thenReturn(valueOperations);
        when(valueOperations.get("otp:code:+15551234567")).thenReturn(null);

        OtpService otpService = new OtpService(redisTemplate, otpSenderPort);
        boolean result = otpService.verifyOtp("+15551234567", "123456");

        assertThat(result).isFalse();
    }
}
