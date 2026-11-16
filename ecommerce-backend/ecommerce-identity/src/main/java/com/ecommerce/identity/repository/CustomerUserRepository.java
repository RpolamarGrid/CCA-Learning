package com.ecommerce.identity.repository;

import com.ecommerce.identity.entity.CustomerUser;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CustomerUserRepository extends JpaRepository<CustomerUser, Long> {
    Optional<CustomerUser> findByPhoneNumber(String phoneNumber);
}
