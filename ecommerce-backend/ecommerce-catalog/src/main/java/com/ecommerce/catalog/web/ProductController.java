package com.ecommerce.catalog.web;

import com.ecommerce.catalog.dto.ProductResponse;
import com.ecommerce.catalog.service.ProductService;
import com.ecommerce.common.dto.ApiResponse;
import com.ecommerce.common.dto.PageResponse;
import java.math.BigDecimal;
import org.springframework.data.domain.Pageable;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * Public, unauthenticated product browsing. REST conventions: plural noun
 * resource, pagination via page/size query params, nested detail by id.
 */
@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final ProductService productService;

    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    @GetMapping
    public ApiResponse<PageResponse<ProductResponse>> list(
            @RequestParam(required = false) String name,
            @RequestParam(required = false) Long categoryId,
            @RequestParam(required = false) BigDecimal minPrice,
            @RequestParam(required = false) BigDecimal maxPrice,
            Pageable pageable) {
        var page = productService.list(name, categoryId, minPrice, maxPrice, pageable)
                .map(ProductResponse::from);
        return ApiResponse.ok(PageResponse.from(page));
    }

    @GetMapping("/{id}")
    public ApiResponse<ProductResponse> getById(@PathVariable Long id) {
        return ApiResponse.ok(ProductResponse.from(productService.getById(id)));
    }
}
