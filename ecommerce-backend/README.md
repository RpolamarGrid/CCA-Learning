# ecommerce-backend

A greenfield, modular-monolith Spring Boot backend implementing one full e-commerce vertical
slice: product listing -> product detail -> OTP login -> add to cart -> checkout -> mock PhonePe
payment -> order confirmed -> async inventory decrement.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full architecture, pattern catalog,
security model, event-flow diagrams, payment gateway contract, and scaling discussion. See
[`docs/adr/`](docs/adr/) for the individual architecture decision records.

## Modules

| Module | Purpose |
|---|---|
| `ecommerce-common` | shared DTOs, exceptions, base JPA entity |
| `ecommerce-notification` | OTP sender port + mock adapter |
| `ecommerce-identity` | admin + customer (OTP) auth, JWT |
| `ecommerce-catalog` | products/categories, public browse + admin CRUD |
| `ecommerce-inventory` | stock, async decrement on order confirmation |
| `ecommerce-cart` | Redis-backed cart |
| `ecommerce-payment` | payment gateway abstraction + PhonePe sandbox adapter |
| `ecommerce-order` | order state machine, checkout orchestration, payment webhook |
| `ecommerce-app` | bootstrap, security config, application.yml, SSE admin stream |

## Prerequisites

- JDK 17+ (project compiles to bytecode release 17 regardless of the JDK used to build - Spring
  Boot 3.3 officially supports 17/21 LTS)
- Maven 3.9+
- Docker (for `docker-compose` Postgres/Redis locally, and for the optional Testcontainers
  integration test)

## Run locally

```bash
cp .env.example .env
# edit .env with your own JWT signing key, etc. (never commit real secrets)

docker-compose up -d        # starts Postgres + Redis

mvn clean install -DskipTests
cd ecommerce-app
mvn spring-boot:run
# or: java -jar target/ecommerce-app-1.0.0-SNAPSHOT.jar
```

The app starts on `http://localhost:8080` with the `local` Spring profile (reads Postgres/Redis
connection details from environment variables with docker-compose defaults baked in).

## Run tests

```bash
mvn clean verify
```

This runs all unit tests. The one Testcontainers-based Postgres integration test
(`ProductRepositoryIT`) is tagged `@Tag("integration")` and excluded from the default run so it
never blocks environments without a reliable Docker daemon. To run it explicitly:

```bash
cd ecommerce-app
mvn verify -Pintegration
```

## Secrets

Copy `.env.example` to `.env` and fill in real values. Never commit `.env`. Required secrets:

- `JWT_SIGNING_KEY` - HMAC signing key for access/refresh JWTs
- `PHONEPE_MERCHANT_ID`, `PHONEPE_SALT_KEY`, `PHONEPE_SALT_INDEX` - PhonePe sandbox credentials
  (placeholders only in this repo; never real credentials)

## API overview

All responses are wrapped in `{ success, data, error, timestamp }`. See
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md#8-rest-api-conventions) for conventions.

- `GET /api/products`, `GET /api/products/{id}` - public product browsing
- `POST /api/admin/products` (and PUT/DELETE) - admin-only product CRUD
- `POST /api/auth/admin/login` - admin username/password login
- `POST /api/auth/customer/otp/send`, `POST /api/auth/customer/otp/verify` - customer OTP login
- `GET /api/cart`, `POST /api/cart/items`, `DELETE /api/cart/items/{productId}` - customer cart
- `POST /api/orders/checkout` - checkout orchestration (payment -> order confirmed -> async
  inventory decrement)
- `POST /api/payments/phonepe/webhook` - PhonePe payment callback (idempotent)
- `GET /admin/stream/orders` - SSE stream of order status changes (admin only)

## CI/CD

See `.github/workflows/ci.yml`: build + test on every push/PR to `main`, build a Docker image via
the multi-stage `Dockerfile`, and a stubbed `deploy` job gated on `main`.

## Claude Code project scaffolding

`.claude/rules/`, `.claude/skills/`, and `.claude/hooks/` document project-specific conventions
(payment gateway abstraction boundary, security invariants, and step-by-step skills for adding a
payment gateway or a product field).
