package com.ecommerce.inventory.entity;

import com.ecommerce.common.entity.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/** @Version (inherited from BaseEntity) gives optimistic locking on concurrent stock decrements. */
@Entity
@Table(name = "inventory")
@Getter
@Setter
@NoArgsConstructor
public class Inventory extends BaseEntity {

    @Column(nullable = false, unique = true)
    private Long productId;

    @Column(nullable = false)
    private int quantityAvailable;
}
