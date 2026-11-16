package com.ecommerce.catalog.spec;

import com.ecommerce.catalog.entity.Product;
import java.math.BigDecimal;
import org.springframework.data.jpa.domain.Specification;

/**
 * Specification pattern for composable, type-safe product filtering -
 * avoids an explosion of ad-hoc repository finder methods per filter combo.
 */
public final class ProductSpecifications {

    private ProductSpecifications() {
    }

    public static Specification<Product> active() {
        return (root, query, cb) -> cb.isTrue(root.get("active"));
    }

    public static Specification<Product> nameContains(String name) {
        return (root, query, cb) -> name == null ? null
                : cb.like(cb.lower(root.get("name")), "%" + name.toLowerCase() + "%");
    }

    public static Specification<Product> categoryIdEquals(Long categoryId) {
        return (root, query, cb) -> categoryId == null ? null
                : cb.equal(root.get("category").get("id"), categoryId);
    }

    public static Specification<Product> priceBetween(BigDecimal min, BigDecimal max) {
        return (root, query, cb) -> {
            if (min == null && max == null) {
                return null;
            }
            if (min != null && max != null) {
                return cb.between(root.get("price"), min, max);
            }
            return min != null ? cb.ge(root.get("price"), min) : cb.le(root.get("price"), max);
        };
    }
}
