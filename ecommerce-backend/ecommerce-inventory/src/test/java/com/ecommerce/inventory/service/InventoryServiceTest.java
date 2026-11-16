package com.ecommerce.inventory.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.ecommerce.inventory.entity.Inventory;
import com.ecommerce.inventory.event.InventoryShortfallEvent;
import com.ecommerce.inventory.repository.InventoryRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.context.ApplicationEventPublisher;

@ExtendWith(MockitoExtension.class)
class InventoryServiceTest {

    @Mock
    private InventoryRepository inventoryRepository;

    @Mock
    private ApplicationEventPublisher eventPublisher;

    @Test
    void decrementsStockWhenSufficient() {
        InventoryService service = new InventoryService(inventoryRepository, eventPublisher);
        Inventory inventory = new Inventory();
        inventory.setProductId(1L);
        inventory.setQuantityAvailable(10);
        when(inventoryRepository.findByProductId(1L)).thenReturn(java.util.Optional.of(inventory));

        service.decrement(100L, 1L, 3);

        ArgumentCaptor<Inventory> captor = ArgumentCaptor.forClass(Inventory.class);
        verify(inventoryRepository).save(captor.capture());
        assertThat(captor.getValue().getQuantityAvailable()).isEqualTo(7);
    }

    @Test
    void publishesShortfallEventWhenInsufficientStock() {
        InventoryService service = new InventoryService(inventoryRepository, eventPublisher);
        Inventory inventory = new Inventory();
        inventory.setProductId(1L);
        inventory.setQuantityAvailable(2);
        when(inventoryRepository.findByProductId(1L)).thenReturn(java.util.Optional.of(inventory));

        service.decrement(100L, 1L, 5);

        verify(eventPublisher).publishEvent(any(InventoryShortfallEvent.class));
    }
}
