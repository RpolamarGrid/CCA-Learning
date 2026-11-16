package com.ecommerce.cart.service;

import com.ecommerce.cart.model.Cart;
import com.ecommerce.cart.model.CartItem;
import com.ecommerce.catalog.entity.Product;
import com.ecommerce.catalog.service.ProductService;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

/**
 * Cart state is Redis-backed (not relational): carts are ephemeral, high-churn,
 * read/written far more often than orders, and naturally expire via TTL.
 */
@Service
public class CartService {

    private static final Duration CART_TTL = Duration.ofDays(7);
    private static final String KEY_PREFIX = "cart:";

    private final RedisTemplate<String, Cart> redisTemplate;
    private final ProductService productService;

    public CartService(RedisTemplate<String, Cart> redisTemplate, ProductService productService) {
        this.redisTemplate = redisTemplate;
        this.productService = productService;
    }

    public Cart getCart(String customerId) {
        Cart cart = redisTemplate.opsForValue().get(KEY_PREFIX + customerId);
        return cart != null ? cart : new Cart(customerId);
    }

    public Cart addItem(String customerId, Long productId, int quantity) {
        Cart cart = getCart(customerId);
        Product product = productService.getById(productId);
        List<CartItem> items = new ArrayList<>(cart.getItems());
        items.removeIf(item -> item.productId().equals(productId));
        items.add(new CartItem(product.getId(), product.getName(), product.getPrice(), quantity));
        cart.setItems(items);
        save(cart);
        return cart;
    }

    public Cart removeItem(String customerId, Long productId) {
        Cart cart = getCart(customerId);
        List<CartItem> items = new ArrayList<>(cart.getItems());
        items.removeIf(item -> item.productId().equals(productId));
        cart.setItems(items);
        save(cart);
        return cart;
    }

    public void clear(String customerId) {
        redisTemplate.delete(KEY_PREFIX + customerId);
    }

    private void save(Cart cart) {
        redisTemplate.opsForValue().set(KEY_PREFIX + cart.getCustomerId(), cart, CART_TTL);
    }
}
