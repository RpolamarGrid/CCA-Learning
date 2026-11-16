package com.ecommerce.cart.web;

import com.ecommerce.cart.dto.AddCartItemRequest;
import com.ecommerce.cart.model.Cart;
import com.ecommerce.cart.service.CartService;
import com.ecommerce.common.dto.ApiResponse;
import jakarta.validation.Valid;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/cart")
public class CartController {

    private final CartService cartService;

    public CartController(CartService cartService) {
        this.cartService = cartService;
    }

    @GetMapping
    public ApiResponse<Cart> view(Authentication authentication) {
        return ApiResponse.ok(cartService.getCart(authentication.getName()));
    }

    @PostMapping("/items")
    public ApiResponse<Cart> addItem(Authentication authentication, @Valid @RequestBody AddCartItemRequest request) {
        return ApiResponse.ok(cartService.addItem(authentication.getName(), request.productId(), request.quantity()));
    }

    @DeleteMapping("/items/{productId}")
    public ApiResponse<Cart> removeItem(Authentication authentication, @PathVariable Long productId) {
        return ApiResponse.ok(cartService.removeItem(authentication.getName(), productId));
    }
}
