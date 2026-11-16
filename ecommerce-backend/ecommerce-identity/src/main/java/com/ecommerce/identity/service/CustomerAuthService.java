package com.ecommerce.identity.service;

import com.ecommerce.common.exception.UnauthorizedException;
import com.ecommerce.identity.dto.TokenResponse;
import com.ecommerce.identity.entity.CustomerUser;
import com.ecommerce.identity.repository.CustomerUserRepository;
import com.ecommerce.identity.security.JwtService;
import org.springframework.stereotype.Service;

@Service
public class CustomerAuthService {

    private final OtpService otpService;
    private final CustomerUserRepository customerUserRepository;
    private final JwtService jwtService;

    public CustomerAuthService(OtpService otpService, CustomerUserRepository customerUserRepository, JwtService jwtService) {
        this.otpService = otpService;
        this.customerUserRepository = customerUserRepository;
        this.jwtService = jwtService;
    }

    public void requestOtp(String phoneNumber) {
        otpService.sendOtp(phoneNumber);
    }

    public TokenResponse verifyOtpAndLogin(String phoneNumber, String code) {
        if (!otpService.verifyOtp(phoneNumber, code)) {
            throw new UnauthorizedException("Invalid or expired OTP");
        }
        CustomerUser customer = customerUserRepository.findByPhoneNumber(phoneNumber)
                .orElseGet(() -> {
                    CustomerUser created = new CustomerUser();
                    created.setPhoneNumber(phoneNumber);
                    return customerUserRepository.save(created);
                });
        String access = jwtService.generateAccessToken(customer.getPhoneNumber(), customer.getRole());
        String refresh = jwtService.generateRefreshToken(customer.getPhoneNumber(), customer.getRole());
        return new TokenResponse(access, refresh, customer.getRole());
    }
}
