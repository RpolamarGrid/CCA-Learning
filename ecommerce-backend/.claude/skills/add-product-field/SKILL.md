# Skill: Add a new Product field

1. Add the field to `Product` entity (`ecommerce-catalog/.../entity/Product.java`) with
   appropriate JPA column annotations.
2. If using a schema-migration tool (Flyway/Liquibase) in your environment, add a migration
   script; this project currently relies on `spring.jpa.hibernate.ddl-auto=update` for local/dev,
   so document any production migration plan separately.
3. Update `ProductResponse` (read DTO) to expose the new field.
4. Update `ProductUpsertRequest` (write DTO) with the new field and any `@Valid` Bean Validation
   constraints (e.g. `@NotBlank`, `@DecimalMin`).
5. Update `ProductService.applyRequest()` to map the new field from request to entity.
6. If the field should be filterable, add a new `Specification<Product>` method in
   `ProductSpecifications` and wire it into `ProductService.list()` and `ProductController`.
7. Update/add unit tests for `ProductService` and any Specification logic; update the
   Testcontainers integration test if the new field affects persistence behavior.
