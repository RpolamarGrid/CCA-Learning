package com.ecommerce.order.web;

import com.ecommerce.common.dto.ApiResponse;
import com.ecommerce.order.dto.CheckoutResponse;
import com.ecommerce.order.service.CheckoutService;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/orders")
public class CheckoutController {

    private final CheckoutService checkoutService;

    public CheckoutController(CheckoutService checkoutService) {
        this.checkoutService = checkoutService;
    }

    @PostMapping("/checkout")
    public ApiResponse<CheckoutResponse> checkout(Authentication authentication) {
        return ApiResponse.ok(checkoutService.checkout(authentication.getName()));
    }
}
