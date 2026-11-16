package com.ecommerce.identity.entity;

import com.ecommerce.common.entity.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * Customer identity created lazily on first successful OTP verification.
 * Guests remain unauthenticated and need no entity.
 */
@Entity
@Table(name = "customer_users")
@Getter
@Setter
@NoArgsConstructor
public class CustomerUser extends BaseEntity {

    @Column(nullable = false, unique = true)
    private String phoneNumber;

    @Column(nullable = false)
    private String role = "ROLE_CUSTOMER";
}
