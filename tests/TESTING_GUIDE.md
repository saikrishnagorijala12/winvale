# Winvale API Test Suite Documentation

This document provides a comprehensive guide to the API test suite developed for the Winvale Analysis Platform.

##  Quick Start

### Prerequisites
- **Python 3.10+** (Verified compatible)
- Requirements installed in your virtual environment: `pip install pytest fastapi httpx sqlalchemy redis`

### Running All Tests
```bash
./venv/bin/python -m pytest tests/ -v
```

### Running Specific Areas
- **Routes**: `./venv/bin/python -m pytest tests/test_routes/ -v`
- **Services**: `./venv/bin/python -m pytest tests/test_services/ -v`
- **Utils**: `./venv/bin/python -m pytest tests/test_utils/ -v`
- **Schemas**: `./venv/bin/python -m pytest tests/test_schemas/ -v`
- **Auth**: `./venv/bin/python -m pytest tests/test_auth/ -v`

### Running Specific Tests
- **By Module**: `./venv/bin/python -m pytest tests/test_routes/test_user_routes.py -v`
- **By Class**: `./venv/bin/python -m pytest tests/test_routes/test_user_routes.py::TestGetMe -v`
- **By Method**: `./venv/bin/python -m pytest tests/test_routes/test_user_routes.py::TestGetMe::test_success -v`

---

##  Test Architecture

The suite is designed as **Mock-based Integration Tests**. It tests the API endpoints (FastAPI) and supporting logic while mocking external dependencies to ensure speed and isolation.

### Key Components

1.  **`tests/conftest.py`**: The "Heart" of the test suite.
    - **Redis Mock**: Automatically intercepts all Redis calls via `FakeRedis`.
    - **Auth Mock**: Patches Cognito JWT verification. Requests are authenticated as a fake user.
    - **Test Clients**: Provides three distinct fixtures:
        - `client`: Admin user.
        - `regular_client`: Regular user.
        - `unauth_client`: Unauthenticated user.
    - **Database Mock**: Provides a `mock_db` fixture (`MagicMock`) for SQLAlchemy `Session`.

2.  **Test Isolation & Global State**:
    The suite includes reset helpers to ensure clean state between tests:
    - `_reset_jwks_cache()`: Resets the Cognito JWKS cache.
    - `_reset_redis_backoff()`: Resets the Redis failure backoff timer.
    These are called automatically via `pytest` fixtures in their respective test areas.

3.  **Service-Level Mocking**:
    Most route tests patch functions in the `app/services/` layer to test API logic independently of the database.

---

##  Directory Structure

The suite currently contains **175 tests** covering:

```text
tests/
├── conftest.py                # Global fixtures (auth, db, redis mocks)
├── test_auth/                 # Cognito & JWKS caching logic
├── test_routes/               # Comprehensive API endpoint coverage (10+ modules)
├── test_schemas/              # Pydantic model validation & normalization
├── test_services/             # Business logic & batch processing
└── test_utils/                # Cache, upload, and data normalization helpers
```

---

## Database Strategy

### Current: Mocked (Default)
The tests use the `mock_db` fixture (`MagicMock`). 
- **Pros**: Blazing fast (<6 seconds for 175 tests), zero setup.
- **Cons**: Does not verify raw SQL queries or complex DB constraints.

### Option: Real PostgreSQL
To use a real database (e.g., `winvale_test_db`):
1.  Update the `get_db` override in `tests/conftest.py`.
2.  Import `Base` and call `Base.metadata.create_all(engine)` in a session-scoped fixture.
3.  Remove service-layer patches to allow the code to reach the database.

---

##  Standardized Error Handling

Every test class verifies:
- **Success Paths**: `200 OK`, `201 Created`, or `202 Accepted`.
- **Error Paths**: `400 Bad Request`, `404 Not Found`, `409 Conflict`.
- **Validation**: `422 Unprocessable Content` (Triggered by Pydantic/FastAPI).
- **Security**: `401 Unauthorized` (Missing token) and `403 Forbidden` (RBAC).

---

## Maintenance Notes
- **Warnings**: The suite is currently warning-free. Avoid using deprecated constants like `HTTP_422_UNPROCESSABLE_ENTITY` (use `HTTP_422_UNPROCESSABLE_CONTENT`).
- **Redis**: The `retry_on_timeout` parameter is deprecated; timeout behavior is handled by default in the current configuration.
