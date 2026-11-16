package com.ecommerce.order.service;

import com.ecommerce.order.dto.PhonePeWebhookRequest;
import com.ecommerce.order.entity.Order;
import com.ecommerce.order.entity.ProcessedWebhookEvent;
import com.ecommerce.order.repository.OrderRepository;
import com.ecommerce.order.repository.ProcessedWebhookEventRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Idempotent webhook handling: a unique constraint on providerTransactionId
 * (enforced via {@link ProcessedWebhookEventRepository}) means a duplicated
 * PhonePe callback is a safe no-op rather than a double-processed order.
 */
@Service
public class PaymentWebhookService {

    private final ProcessedWebhookEventRepository processedWebhookEventRepository;
    private final OrderRepository orderRepository;

    public PaymentWebhookService(ProcessedWebhookEventRepository processedWebhookEventRepository, OrderRepository orderRepository) {
        this.processedWebhookEventRepository = processedWebhookEventRepository;
        this.orderRepository = orderRepository;
    }

    @Transactional
    public void handle(PhonePeWebhookRequest request) {
        if (processedWebhookEventRepository.existsByProviderTransactionId(request.providerTransactionId())) {
            return;
        }
        ProcessedWebhookEvent event = new ProcessedWebhookEvent();
        event.setProviderTransactionId(request.providerTransactionId());
        processedWebhookEventRepository.save(event);

        orderRepository.findByPaymentTransactionId(request.providerTransactionId())
                .ifPresent(this::acknowledgeOrder);
    }

    private void acknowledgeOrder(Order order) {
        // Order already progressed synchronously in CheckoutService for this demo flow;
        // a real async PhonePe redirect flow would drive the PAID transition from here instead.
    }
}
