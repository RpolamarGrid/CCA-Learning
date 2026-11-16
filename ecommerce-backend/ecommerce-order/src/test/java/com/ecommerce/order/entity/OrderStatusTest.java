package com.ecommerce.order.entity;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

class OrderStatusTest {

    @Test
    void happyPathTransitionsAreAllowed() {
        assertThat(OrderStatus.CREATED.canTransitionTo(OrderStatus.PAID)).isTrue();
        assertThat(OrderStatus.PAID.canTransitionTo(OrderStatus.INVENTORY_RESERVED)).isTrue();
        assertThat(OrderStatus.INVENTORY_RESERVED.canTransitionTo(OrderStatus.CONFIRMED)).isTrue();
    }

    @Test
    void terminalStatesHaveNoOutgoingTransitions() {
        assertThat(OrderStatus.FAILED.canTransitionTo(OrderStatus.CREATED)).isFalse();
        assertThat(OrderStatus.COMPENSATED.canTransitionTo(OrderStatus.CONFIRMED)).isFalse();
    }

    @Test
    void cannotSkipStates() {
        assertThat(OrderStatus.CREATED.canTransitionTo(OrderStatus.CONFIRMED)).isFalse();
        assertThat(OrderStatus.CREATED.canTransitionTo(OrderStatus.INVENTORY_RESERVED)).isFalse();
    }
}
