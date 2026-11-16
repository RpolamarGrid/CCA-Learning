package com.ecommerce.order.repository;

import com.ecommerce.order.entity.ProcessedWebhookEvent;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProcessedWebhookEventRepository extends JpaRepository<ProcessedWebhookEvent, Long> {
    boolean existsByProviderTransactionId(String providerTransactionId);
}
