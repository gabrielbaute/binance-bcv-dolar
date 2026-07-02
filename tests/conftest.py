"""
Test configuration, fixtures, and shared helpers.

We override environment variables before any app module is imported so that
the global ``Config`` singleton and ``db_manager`` are built with test-safe
values.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

# ---------------------------------------------------------------------------
#  Force test environment BEFORE any ``app.`` import
# ---------------------------------------------------------------------------
os.environ.setdefault("NTFY_TOPIC", "test-topic")
os.environ.setdefault("NTFY_URL", "https://ntfy.example.com")
os.environ.setdefault("BINANCE_EXTRA_FIATS", "")
os.environ.setdefault("BINANCE_EXTRA_CRON", "0 */3 * * *")
os.environ.setdefault("BINANCE_VES_CRON", "*/30 * * * *")
os.environ.setdefault("BCV_CRON", "0 0 * * *")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

# Now safe to import app internals
from app.config import Config, config as live_config  # noqa: E402
from app.database import db_manager as live_db_manager  # noqa: E402
from app.database.database_manager import DatabaseManager  # noqa: E402
from app.api.dependencies import get_db_session  # noqa: E402
from app.api.app_factory import create_app  # noqa: E402

# ---------------------------------------------------------------------------
#  pytest-asyncio
# ---------------------------------------------------------------------------
pytest_plugins = ("pytest_asyncio",)


# ===================================================================
#  In-memory database fixtures
# ===================================================================


@pytest_asyncio.fixture(scope="session")
async def in_memory_engine():
    """Create a shared in-memory async engine for the test session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(in_memory_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a clean async session per test with rollback."""
    session_maker = async_sessionmaker(
        in_memory_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_maker() as session:
        yield session


# ===================================================================
#  Mocked BinanceService / BCVService for API tests
# ===================================================================


@pytest.fixture
def mock_binance_service():
    """Return a fully mocked BinanceService."""
    svc = MagicMock()
    svc.get_real_time_usdt_ves_pair = MagicMock()
    svc.get_real_time_pair = MagicMock()
    svc.get_last_saved_binance_fiat = AsyncMock()
    svc.get_all_saved_binance_pair = AsyncMock()
    svc.get_binance_pair_by_time_range = AsyncMock()
    return svc


@pytest.fixture
def mock_bcv_service():
    """Return a fully mocked BCVService."""
    svc = MagicMock()
    svc.get_real_time_exchange_rate = MagicMock()
    svc.get_exchange_rate = AsyncMock()
    svc.get_currency_exchange_rates_by_range = AsyncMock()
    svc.get_all_currency_registers = AsyncMock()
    return svc


@pytest.fixture
def mock_dolar_service():
    """Return a fully mocked DolarVenezuelaService."""
    svc = MagicMock()
    svc.get_average_dolar_last_register = AsyncMock()
    svc.get_real_time_average_dolar = MagicMock()
    return svc


@pytest.fixture
def mock_fiat_exchange_service():
    """Return a fully mocked FiatExchangeService."""
    svc = MagicMock()
    svc.get_pair = AsyncMock()
    svc.get_real_time_pair = MagicMock()
    svc.get_historical_pair = AsyncMock()
    return svc


# ===================================================================
#  FastAPI test client  (dependency overrides)
# ===================================================================


@pytest.fixture
def app() -> FastAPI:
    """Build the application with test config."""
    _app = create_app(config=live_config)
    return _app


@pytest_asyncio.fixture
async def client(
    app: FastAPI,
    mock_binance_service,
    mock_bcv_service,
    mock_dolar_service,
    mock_fiat_exchange_service,
) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async test client with all services mocked."""

    from app.services import BinanceService, BCVService
    from app.services import DolarVenezuelaService, FiatExchangeService
    from app.api.dependencies import (
        get_binance_service,
        get_bcv_service,
        get_dolar_vzla_service,
        get_fiat_exchange_service,
    )

    app.dependency_overrides[get_binance_service] = lambda: mock_binance_service
    app.dependency_overrides[get_bcv_service] = lambda: mock_bcv_service
    app.dependency_overrides[get_dolar_vzla_service] = lambda: mock_dolar_service
    app.dependency_overrides[get_fiat_exchange_service] = lambda: mock_fiat_exchange_service

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test/api/v1") as ac:
        yield ac

    app.dependency_overrides.clear()


# ===================================================================
#  Sample data builders
# ===================================================================


@pytest.fixture
def sample_bcv_currency_dict():
    from datetime import datetime, timezone
    from uuid import uuid4
    from app.enums import Currency, TradeType

    return {
        "id": uuid4(),
        "currency": Currency.DOLAR,
        "trade_type": TradeType.SELL,
        "rate": 245.55,
        "date": datetime.now(timezone.utc),
    }


@pytest.fixture
def sample_binance_currency_dict():
    from datetime import datetime, timezone
    from uuid import uuid4
    from app.enums import FiatCurrency, BinanceAsset, TradeType

    return {
        "id": uuid4(),
        "fiat": FiatCurrency.VES,
        "asset": BinanceAsset.USDT,
        "trade_type": TradeType.BUY,
        "average_price": 346.97,
        "median_price": 347.00,
        "date": datetime.now(timezone.utc),
    }
