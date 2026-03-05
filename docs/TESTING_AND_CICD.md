# Testing and CI/CD Guide

This document explains how tests work and how the CI/CD pipeline is set up for this project.

---

## Table of Contents

1. [How Tests Work](#how-tests-work)
2. [Running Tests Locally](#running-tests-locally)
3. [Test Structure](#test-structure)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [CI Workflow Details](#ci-workflow-details)
6. [Troubleshooting](#troubleshooting)

---

## How Tests Work

### Overview

Tests use **pytest** with **pytest-asyncio** for async API tests and **httpx** as the HTTP client. Tests run against the FastAPI app directly without starting a server (ASGI transport).

### Test Flow

1. **conftest.py** runs first and sets env vars for the test environment (e.g. `DATABASE_URL`, `SUPABASE_URL`).
2. **test_api.py** imports the FastAPI app and creates an `AsyncClient` that talks to the app via ASGI.
3. Each test makes HTTP requests to endpoints and asserts the response.

### What Gets Tested

- **Root endpoint** (`/`) – Returns welcome message.
- **Health endpoint** (`/api/v1/health`) – Returns status.

These are smoke tests that verify the app starts and basic routes work. Add more tests in `tests/` as needed.

---

## Running Tests Locally

### Prerequisites

- Python 3.12+
- PostgreSQL running (for tests that hit the DB)

### Install Test Dependencies

```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio httpx
```

### Run All Tests

```bash
pytest tests/ -v
```

### Run With Verbose Output

```bash
pytest tests/ -v --tb=short
```

### Run a Single Test File

```bash
pytest tests/test_api.py -v
```

### Run a Single Test

```bash
pytest tests/test_api.py::test_root -v
```

### Environment Variables

Tests use `conftest.py` to set defaults. For local runs, you can override with:

- `DATABASE_URL` – PostgreSQL connection string (default: `postgresql://postgres:postgres@localhost:5432/test`)
- `SUPABASE_URL` – Supabase URL (default: `https://test.supabase.co`)
- `SERVICE_ROLE_KEY` – Supabase key (default: `test-key-for-ci`)
- `REDIS_HOST` – Redis host (default: `localhost`)

For local tests that hit the DB, ensure PostgreSQL is running and the test DB exists.

---

## Test Structure

```
tests/
├── __init__.py
├── conftest.py      # Pytest config, env vars, shared fixtures
└── test_api.py      # API smoke tests
```

### conftest.py

- Sets `DATABASE_URL`, `SUPABASE_URL`, `SERVICE_ROLE_KEY`, `REDIS_HOST` before imports.
- Uses `setdefault` so existing env vars are not overwritten.

### test_api.py

- **client** fixture – Returns an `httpx.AsyncClient` configured for the app.
- **test_root** – Tests `GET /` returns 200 and welcome message.
- **test_health** – Tests `GET /api/v1/health` returns 200 and `status: ok`.

### Adding New Tests

1. Create `tests/test_<feature>.py`.
2. Use the `client` fixture from `test_api.py` or define your own.
3. For async tests, use `@pytest.mark.asyncio` and `async def`.

```python
@pytest.mark.asyncio
async def test_my_endpoint(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
```

---

## CI/CD Pipeline

### Overview

GitHub Actions runs on every push and pull request to `main`, `staging`, and `tes_app` branches. The pipeline has three jobs:

| Job | Purpose |
|-----|---------|
| **Lint** | Runs Ruff to check code style and errors |
| **Test** | Runs pytest with a PostgreSQL service |
| **Docker** | Builds the Docker image |

All jobs run in parallel. The workflow fails if any job fails.

### Trigger Branches

- `main`
- `staging`
- `tes_app`

### Workflow File

- `.github/workflows/ci.yml`

---

## CI Workflow Details

### 1. Lint Job

- **Runner:** `ubuntu-latest`
- **Python:** 3.12
- **Steps:**
  1. Checkout code
  2. Install Ruff
  3. Run `ruff check . --output-format=github`

Ruff config is in `ruff.toml`.

### 2. Test Job

- **Runner:** `ubuntu-latest`
- **Services:** PostgreSQL 16 (alpine)
  - User: `postgres`
  - Password: `postgres`
  - Database: `test`
  - Port: `5432`
- **Steps:**
  1. Checkout code
  2. Set up Python 3.12
  3. Install `requirements.txt` + `pytest`, `pytest-asyncio`, `httpx`
  4. Run `pytest tests/ -v --tb=short` with CI env vars

**CI Environment Variables:**

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/test` |
| `SUPABASE_URL` | `https://test.supabase.co` |
| `SERVICE_ROLE_KEY` | `test-key-for-ci` |
| `REDIS_HOST` | `localhost` |

### 3. Docker Job

- **Runner:** `ubuntu-latest`
- **Steps:**
  1. Checkout code
  2. Set up Docker Buildx
  3. Build image with tag `fastapi-template:ci` (no push, cache only)

### Viewing CI Results

- **GitHub:** Repo → Actions → select workflow run
- **PR:** Checks appear on the PR; green = pass, red = fail

---

## Troubleshooting

### Tests fail locally with "connection refused"

- Ensure PostgreSQL is running.
- Create the test DB: `createdb test`
- Or use Docker: `docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:16-alpine`

### Ruff fails in CI

- Run `ruff check .` locally; fix reported issues.
- Update `ruff.toml` if you need to ignore or adjust rules.

### Docker build fails in CI

- Run `docker build -t fastapi-template .` locally.
- Check `Dockerfile` and `.dockerignore`.

### Tests pass locally but fail in CI

- CI uses PostgreSQL 16; ensure local DB is compatible.
- Check that no local-only env vars or paths are required.
