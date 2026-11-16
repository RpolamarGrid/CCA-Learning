package com.ecommerce.identity.web;

import com.ecommerce.common.dto.ApiResponse;
import com.ecommerce.identity.dto.OtpSendRequest;
import com.ecommerce.identity.dto.OtpVerifyRequest;
import com.ecommerce.identity.dto.TokenResponse;
import com.ecommerce.identity.service.CustomerAuthService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/auth/customer")
public class CustomerAuthController {

    private final CustomerAuthService customerAuthService;

    public CustomerAuthController(CustomerAuthService customerAuthService) {
        this.customerAuthService = customerAuthService;
    }

    @PostMapping("/otp/send")
    public ApiResponse<Void> sendOtp(@Valid @RequestBody OtpSendRequest request) {
        customerAuthService.requestOtp(request.phoneNumber());
        return ApiResponse.ok(null);
    }

    @PostMapping("/otp/verify")
    public ApiResponse<TokenResponse> verifyOtp(@Valid @RequestBody OtpVerifyRequest request) {
        return ApiResponse.ok(customerAuthService.verifyOtpAndLogin(request.phoneNumber(), request.code()));
    }
}
