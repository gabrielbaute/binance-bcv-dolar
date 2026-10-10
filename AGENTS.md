# Repository Guidelines

## Project overview and architecture

This service collects BCV official rates and Binance P2P USDT/fiat prices, stores snapshots in SQLite, and exposes current and historical data through FastAPI and a web dashboard. `app/main.py` creates the application, initializes the database, and starts APScheduler in the FastAPI lifespan. Scheduled jobs call services, which fetch and process provider data and use controllers to persist it. Optional ntfy notifications report updates and failures. Additional Binance fiats are selected through `BINANCE_EXTRA_FIATS`.

## Repository structure

Change `app/api/routes/` and `app/schemas/` for HTTP contracts; `app/services/` for provider access and rate calculations; `app/controllers/` and `app/database/` for persistence; `app/scheduler/` for jobs; and `app/config/` for settings and logging. `app/migration/` contains a separate database migration CLI. The dashboard source is in `app/ui/src/`, with templates and static assets under `app/ui/`. Tests belong in `tests/test_*.py`. Review `README.md`, `pyproject.toml`, `uv.lock`, Docker files, and `.github/workflows/` before changing related behavior.

## Development workflow

Use Python 3.13 and `uv sync --group dev` to install locked dependencies. Run `uv run uvicorn app.main:app --reload` locally; startup creates missing tables and starts real jobs. Run `uv run pytest` for tests, `uv run ruff check app tests`, `uv run black --check app tests`, and `uv run mypy app` for configured checks. For UI changes, run `npm install` and `npm run build:ui`. Docker development uses `docker compose -f docker-compose.dev.yml up --build`. Do not claim a check passed unless it ran.

## Coding standards and API conventions

Follow existing Python names and four-space indentation. Black and Ruff use 100-character lines. Add useful type hints; keep functions focused, avoid duplicated logic and new dependencies without need, and use async for actual asynchronous I/O. Preserve `/api/v1` routes, status codes, response schemas, and clients. Validate inputs and provider payloads; map failures to safe API errors without leaking tracebacks or secrets. Update tests and docs for contract changes.

## External integrations, scheduler, and concurrency

Keep provider and ntfy settings in `app/config/`. Set finite request timeouts; use bounded retries and backoff when justified. Never invent a rate or replace missing data with zero; preserve monetary precision and distinguish absent, failed, and stale observations. Mock external HTTP in unit tests. APScheduler runs in `app/main.py` with configurable BCV, VES, and extra-fiat cron expressions. Check overlap, idempotency, duplicate rows, and multi-worker behavior before changing jobs; never start real jobs in tests.

## Database, observability, and security

SQLite uses async SQLAlchemy/SQLModel sessions and WAL; startup `create_all` creates missing tables, while `app/migration/` handles explicit legacy migration. Do not drop or recreate existing databases. Keep writes transactional, consider locks, and use SQLite's backup API for consistent WAL backups. Persist database and logs in writable directories for the nonprivileged container user. Never commit `.env`, `.db`, `.db-wal`, `.db-shm`, logs, or private data. Keep console and rotating-file logging useful for provider and scheduler failures without recording credentials.

## Testing, deployment, and change management

Pytest uses async fixtures, in-memory SQLite, and mocked services in `tests/conftest.py`; cover calculations, historical dates and time zones, provider errors, timeouts, and malformed data. The Dockerfile runs on port 8000 as UID 1000 and publishes through the GHCR workflow. Healthchecks use `/api/v1/health`; Compose and the image persist data at `/app/instance` and logs at `/app/logs`. Run one application worker unless scheduler leadership is coordinated across processes. Dokploy, Cloudflare Tunnel, and Traefik are production-environment details, not configured here. For each change, inspect affected code, make the smallest coherent edit, add relevant tests, run checks, document behavior changes, and report results and remaining risks. Avoid unrelated refactors and automatic commits.
