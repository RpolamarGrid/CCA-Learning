package com.ecommerce.notification;

/**
 * Port (Strategy/Adapter boundary) for delivering OTP codes to customers.
 * Real SMS providers (Twilio, MSG91, etc.) implement this in production;
 * never call a provider SDK directly from application code.
 */
public interface OtpSenderPort {

    void sendOtp(String phoneNumber, String otpCode);
}
