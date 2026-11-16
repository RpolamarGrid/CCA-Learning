package com.ecommerce.catalog.dto;

import com.ecommerce.catalog.entity.Product;
import java.math.BigDecimal;

public record ProductResponse(Long id, String name, String description, BigDecimal price, Long categoryId, boolean active) {

    public static ProductResponse from(Product product) {
        Long categoryId = product.getCategory() != null ? product.getCategory().getId() : null;
        return new ProductResponse(product.getId(), product.getName(), product.getDescription(),
                product.getPrice(), categoryId, product.isActive());
    }
}
