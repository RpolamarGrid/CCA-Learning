package com.ecommerce.identity.service;

import com.ecommerce.common.exception.BusinessException;
import com.ecommerce.notification.OtpSenderPort;
import java.security.SecureRandom;
import java.time.Duration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

/**
 * OTP codes live only in Redis with a TTL - never persisted to the relational DB.
 * This guarantees automatic expiry/cleanup and avoids ever storing a usable-login
 * secret in a durable store that could be backed up, replicated, or queried later.
 */
@Service
public class OtpService {

    private static final Logger log = LoggerFactory.getLogger(OtpService.class);
    private static final Duration OTP_TTL = Duration.ofMinutes(5);
    private static final Duration SEND_RATE_LIMIT_WINDOW = Duration.ofMinutes(1);
    private static final int MAX_SENDS_PER_WINDOW = 3;

    private final StringRedisTemplate redisTemplate;
    private final OtpSenderPort otpSenderPort;
    private final SecureRandom secureRandom = new SecureRandom();

    public OtpService(StringRedisTemplate redisTemplate, OtpSenderPort otpSenderPort) {
        this.redisTemplate = redisTemplate;
        this.otpSenderPort = otpSenderPort;
    }

    public void sendOtp(String phoneNumber) {
        String rateLimitKey = "otp:rate:" + phoneNumber;
        Long attempts = redisTemplate.opsForValue().increment(rateLimitKey);
        if (attempts != null && attempts == 1L) {
            redisTemplate.expire(rateLimitKey, SEND_RATE_LIMIT_WINDOW);
        }
        if (attempts != null && attempts > MAX_SENDS_PER_WINDOW) {
            throw new BusinessException("OTP_RATE_LIMITED", "Too many OTP requests, try again later");
        }

        String code = String.format("%06d", secureRandom.nextInt(1_000_000));
        redisTemplate.opsForValue().set("otp:code:" + phoneNumber, code, OTP_TTL);
        otpSenderPort.sendOtp(phoneNumber, code);
    }

    public boolean verifyOtp(String phoneNumber, String code) {
        String key = "otp:code:" + phoneNumber;
        String stored = redisTemplate.opsForValue().get(key);
        if (stored == null) {
            log.info("OTP verification failed for {}: expired or not requested", phoneNumber);
            return false;
        }
        boolean matches = stored.equals(code);
        if (matches) {
            redisTemplate.delete(key);
        }
        return matches;
    }
}
