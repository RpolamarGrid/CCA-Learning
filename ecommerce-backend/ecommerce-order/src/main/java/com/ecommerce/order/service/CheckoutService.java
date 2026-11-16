package com.ecommerce.order.service;

import com.ecommerce.cart.model.Cart;
import com.ecommerce.cart.model.CartItem;
import com.ecommerce.cart.service.CartService;
import com.ecommerce.common.exception.BusinessException;
import com.ecommerce.order.dto.CheckoutResponse;
import com.ecommerce.order.entity.Order;
import com.ecommerce.order.entity.OrderItem;
import com.ecommerce.order.entity.OrderStatus;
import com.ecommerce.order.event.OrderConfirmedEvent;
import com.ecommerce.order.event.OrderStatusChangedEvent;
import com.ecommerce.order.repository.OrderRepository;
import com.ecommerce.payment.dto.PaymentInitiationResult;
import com.ecommerce.payment.dto.PaymentStatus;
import com.ecommerce.payment.gateway.PaymentGatewayFactory;
import java.util.List;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Checkout orchestration: validate cart -> create order -> initiate payment ->
 * on success publish {@link OrderConfirmedEvent} (consumed async by inventory).
 * Depends only on {@link PaymentGatewayFactory}/{@link com.ecommerce.payment.gateway.PaymentGateway},
 * never a concrete provider SDK (see .claude/rules/payment-gateway.md).
 */
@Service
public class CheckoutService {

    private final CartService cartService;
    private final OrderRepository orderRepository;
    private final PaymentGatewayFactory paymentGatewayFactory;
    private final ApplicationEventPublisher eventPublisher;
    private final String defaultGateway;
    private final String callbackUrl;

    public CheckoutService(
            CartService cartService,
            OrderRepository orderRepository,
            PaymentGatewayFactory paymentGatewayFactory,
            ApplicationEventPublisher eventPublisher,
            @Value("${app.payment.default-gateway:PHONEPE}") String defaultGateway,
            @Value("${app.payment.callback-url:http://localhost:8080/api/payments/phonepe/webhook}") String callbackUrl) {
        this.cartService = cartService;
        this.orderRepository = orderRepository;
        this.paymentGatewayFactory = paymentGatewayFactory;
        this.eventPublisher = eventPublisher;
        this.defaultGateway = defaultGateway;
        this.callbackUrl = callbackUrl;
    }

    @Transactional
    public CheckoutResponse checkout(String customerId) {
        Cart cart = cartService.getCart(customerId);
        if (cart.getItems().isEmpty()) {
            throw new BusinessException("EMPTY_CART", "Cannot checkout an empty cart");
        }

        Order order = new Order();
        order.setCustomerId(customerId);
        order.setTotalAmount(cart.getTotal());
        for (CartItem cartItem : cart.getItems()) {
            OrderItem item = new OrderItem();
            item.setOrder(order);
            item.setProductId(cartItem.productId());
            item.setProductName(cartItem.productName());
            item.setUnitPrice(cartItem.unitPrice());
            item.setQuantity(cartItem.quantity());
            order.getItems().add(item);
        }
        order = orderRepository.save(order);

        PaymentInitiationResult paymentResult = paymentGatewayFactory.resolve(defaultGateway)
                .initiate("ORDER-" + order.getId(), order.getTotalAmount(), callbackUrl);

        if (paymentResult.status() != PaymentStatus.SUCCESS) {
            order.transitionTo(OrderStatus.FAILED);
            orderRepository.save(order);
            eventPublisher.publishEvent(new OrderStatusChangedEvent(order.getId(), order.getStatus()));
            return new CheckoutResponse(order.getId(), order.getStatus(), null);
        }

        order.setPaymentTransactionId(paymentResult.providerTransactionId());
        order.transitionTo(OrderStatus.PAID);
        orderRepository.save(order);
        eventPublisher.publishEvent(new OrderStatusChangedEvent(order.getId(), order.getStatus()));

        order.transitionTo(OrderStatus.INVENTORY_RESERVED);
        orderRepository.save(order);
        eventPublisher.publishEvent(new OrderStatusChangedEvent(order.getId(), order.getStatus()));

        order.transitionTo(OrderStatus.CONFIRMED);
        orderRepository.save(order);
        eventPublisher.publishEvent(new OrderStatusChangedEvent(order.getId(), order.getStatus()));

        cartService.clear(customerId);

        List<OrderConfirmedEvent.OrderLine> lines = order.getItems().stream()
                .map(i -> new OrderConfirmedEvent.OrderLine(i.getProductId(), i.getQuantity()))
                .toList();
        eventPublisher.publishEvent(new OrderConfirmedEvent(order.getId(), lines));

        return new CheckoutResponse(order.getId(), order.getStatus(), paymentResult.redirectUrl());
    }
}
