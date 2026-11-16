package com.ecommerce.identity.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;

public record OtpSendRequest(
        @NotBlank @Pattern(regexp = "^\\+?[0-9]{10,15}$", message = "must be a valid phone number") String phoneNumber) {
}
