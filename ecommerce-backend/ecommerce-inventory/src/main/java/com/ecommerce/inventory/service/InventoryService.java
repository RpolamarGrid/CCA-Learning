package com.ecommerce.inventory.service;

import com.ecommerce.inventory.entity.Inventory;
import com.ecommerce.inventory.event.InventoryShortfallEvent;
import com.ecommerce.inventory.repository.InventoryRepository;
import com.ecommerce.order.event.OrderConfirmedEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.context.event.EventListener;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Asynchronously consumes {@link OrderConfirmedEvent} to decrement stock so
 * checkout response latency is never blocked on inventory writes. Each line
 * is updated in its own transaction; optimistic-lock conflicts (concurrent
 * orders for the same product) are retried-at-caller via normal @Version
 * exception propagation (kept out of scope here for an illustrative demo).
 */
@Service
public class InventoryService {

    private static final Logger log = LoggerFactory.getLogger(InventoryService.class);

    private final InventoryRepository inventoryRepository;
    private final ApplicationEventPublisher eventPublisher;

    public InventoryService(InventoryRepository inventoryRepository, ApplicationEventPublisher eventPublisher) {
        this.inventoryRepository = inventoryRepository;
        this.eventPublisher = eventPublisher;
    }

    @Async
    @EventListener
    public void onOrderConfirmed(OrderConfirmedEvent event) {
        for (OrderConfirmedEvent.OrderLine line : event.lines()) {
            decrement(event.orderId(), line.productId(), line.quantity());
        }
    }

    @Transactional
    public void decrement(Long orderId, Long productId, int quantity) {
        Inventory inventory = inventoryRepository.findByProductId(productId).orElse(null);
        if (inventory == null) {
            log.warn("No inventory record for product {}, skipping decrement for order {}", productId, orderId);
            return;
        }
        if (inventory.getQuantityAvailable() < quantity) {
            eventPublisher.publishEvent(new InventoryShortfallEvent(orderId, productId, quantity, inventory.getQuantityAvailable()));
            return;
        }
        inventory.setQuantityAvailable(inventory.getQuantityAvailable() - quantity);
        inventoryRepository.save(inventory);
    }
}
