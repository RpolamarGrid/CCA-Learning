package com.ecommerce.cart.model;

import java.io.Serializable;
import java.math.BigDecimal;

public record CartItem(Long productId, String productName, BigDecimal unitPrice, int quantity) implements Serializable {

    public BigDecimal lineTotal() {
        return unitPrice.multiply(BigDecimal.valueOf(quantity));
    }
}
