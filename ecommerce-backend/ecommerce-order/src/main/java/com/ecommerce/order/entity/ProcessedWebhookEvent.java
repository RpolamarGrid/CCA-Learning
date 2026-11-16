package com.ecommerce.order.entity;

import com.ecommerce.common.entity.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * Idempotency ledger for payment webhooks: a unique constraint on
 * providerTransactionId guarantees a replayed/duplicated callback from
 * PhonePe never double-confirms or double-decrements inventory.
 */
@Entity
@Table(name = "processed_webhook_events")
@Getter
@Setter
@NoArgsConstructor
public class ProcessedWebhookEvent extends BaseEntity {

    @Column(nullable = false, unique = true)
    private String providerTransactionId;
}
