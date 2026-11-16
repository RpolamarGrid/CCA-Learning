package com.ecommerce.common.dto;

import java.time.Instant;

/**
 * Uniform API response envelope. Every controller returns this shape so
 * clients can parse success/error consistently regardless of endpoint.
 */
public record ApiResponse<T>(boolean success, T data, ApiError error, Instant timestamp) {

    public static <T> ApiResponse<T> ok(T data) {
        return new ApiResponse<>(true, data, null, Instant.now());
    }

    public static <T> ApiResponse<T> error(String code, String message) {
        return new ApiResponse<>(false, null, new ApiError(code, message), Instant.now());
    }

    public record ApiError(String code, String message) {
    }
}
