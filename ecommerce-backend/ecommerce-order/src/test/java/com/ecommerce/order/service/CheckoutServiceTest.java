package com.ecommerce.order.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;

import com.ecommerce.cart.model.Cart;
import com.ecommerce.cart.model.CartItem;
import com.ecommerce.cart.service.CartService;
import com.ecommerce.common.exception.BusinessException;
import com.ecommerce.order.entity.Order;
import com.ecommerce.order.entity.OrderStatus;
import com.ecommerce.order.repository.OrderRepository;
import com.ecommerce.payment.dto.PaymentInitiationResult;
import com.ecommerce.payment.dto.PaymentStatus;
import com.ecommerce.payment.gateway.PaymentGateway;
import com.ecommerce.payment.gateway.PaymentGatewayFactory;
import java.math.BigDecimal;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.context.ApplicationEventPublisher;

@ExtendWith(MockitoExtension.class)
class CheckoutServiceTest {

    @Mock
    private CartService cartService;

    @Mock
    private OrderRepository orderRepository;

    @Mock
    private PaymentGatewayFactory paymentGatewayFactory;

    @Mock
    private PaymentGateway paymentGateway;

    @Mock
    private ApplicationEventPublisher eventPublisher;

    @Test
    void checkoutThrowsForEmptyCart() {
        CheckoutService service = new CheckoutService(cartService, orderRepository, paymentGatewayFactory,
                eventPublisher, "PHONEPE", "http://callback");
        when(cartService.getCart("customer1")).thenReturn(new Cart("customer1"));

        assertThatThrownBy(() -> service.checkout("customer1")).isInstanceOf(BusinessException.class);
    }

    @Test
    void checkoutConfirmsOrderOnSuccessfulPayment() {
        CheckoutService service = new CheckoutService(cartService, orderRepository, paymentGatewayFactory,
                eventPublisher, "PHONEPE", "http://callback");

        Cart cart = new Cart("customer1");
        cart.setItems(java.util.List.of(new CartItem(1L, "Widget", BigDecimal.TEN, 2)));
        when(cartService.getCart("customer1")).thenReturn(cart);
        when(orderRepository.save(any(Order.class))).thenAnswer(invocation -> invocation.getArgument(0));
        when(paymentGatewayFactory.resolve("PHONEPE")).thenReturn(paymentGateway);
        when(paymentGateway.initiate(anyString(), any(BigDecimal.class), anyString()))
                .thenReturn(new PaymentInitiationResult("txn-1", "http://redirect", PaymentStatus.SUCCESS));

        var response = service.checkout("customer1");

        assertThat(response.status()).isEqualTo(OrderStatus.CONFIRMED);
        assertThat(response.paymentRedirectUrl()).isEqualTo("http://redirect");
    }
}
