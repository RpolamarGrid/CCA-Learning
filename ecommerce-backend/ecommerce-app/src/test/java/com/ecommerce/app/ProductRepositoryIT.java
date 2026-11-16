package com.ecommerce.app;

import static org.assertj.core.api.Assertions.assertThat;

import com.ecommerce.catalog.entity.Product;
import com.ecommerce.catalog.repository.ProductRepository;
import java.math.BigDecimal;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.context.ActiveProfiles;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

/**
 * Real-Postgres integration test for the catalog repository layer.
 * Tagged "integration" and excluded from the default `mvn verify` run
 * (see surefire excludedGroups in the parent pom) because it requires a
 * running Docker daemon; run explicitly via `mvn verify -Pintegration`.
 */
@Tag("integration")
@Testcontainers
@SpringBootTest(classes = EcommerceApplication.class)
@ActiveProfiles("test")
class ProductRepositoryIT {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @DynamicPropertySource
    static void datasourceProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
        registry.add("spring.jpa.hibernate.ddl-auto", () -> "create-drop");
    }

    @Autowired
    private ProductRepository productRepository;

    @Test
    void savesAndReloadsProductFromRealPostgres() {
        Product product = new Product();
        product.setName("Integration Test Widget");
        product.setPrice(BigDecimal.valueOf(9.99));
        product.setActive(true);

        Product saved = productRepository.save(product);

        assertThat(productRepository.findById(saved.getId())).isPresent();
    }
}
