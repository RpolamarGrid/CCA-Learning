package com.ecommerce.inventory.event;

public record InventoryShortfallEvent(Long orderId, Long productId, int requested, int available) {
}
