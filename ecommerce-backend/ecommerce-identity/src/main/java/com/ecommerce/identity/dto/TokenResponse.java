package com.ecommerce.identity.dto;

public record TokenResponse(String accessToken, String refreshToken, String role) {
}
