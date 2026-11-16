package com.ecommerce.order.entity;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.ecommerce.common.exception.BusinessException;
import org.junit.jupiter.api.Test;

class OrderTest {

    @Test
    void transitionToUpdatesStatusWhenAllowed() {
        Order order = new Order();
        order.transitionTo(OrderStatus.PAID);
        assertThat(order.getStatus()).isEqualTo(OrderStatus.PAID);
    }

    @Test
    void transitionToThrowsOnIllegalTransition() {
        Order order = new Order();
        order.transitionTo(OrderStatus.PAID);
        order.transitionTo(OrderStatus.INVENTORY_RESERVED);
        order.transitionTo(OrderStatus.CONFIRMED);
        assertThatThrownBy(() -> order.transitionTo(OrderStatus.CREATED))
                .isInstanceOf(BusinessException.class);
    }
}
