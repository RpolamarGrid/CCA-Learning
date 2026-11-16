package com.ecommerce.order.repository;

import com.ecommerce.order.entity.Order;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface OrderRepository extends JpaRepository<Order, Long> {
    Optional<Order> findByPaymentTransactionId(String paymentTransactionId);
}
