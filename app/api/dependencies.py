"""
API Inversion of Control and Dependency Injection Module.

This module encapsulates initialization graphs for operational database sessions,
centralized configurations, and business core services inside the API route lifecycles.
"""

from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Config, config
from app.database import DatabaseManager, db_manager
from app.services import (
    BCVService,
    BinanceService,
    DolarVenezuelaService,
    FiatExchangeService,
    NtfyWebhookService,
)


def get_config_instance() -> Config:
    """
    Provide the globally instantiated configuration state.

    Returns:
        Config: App configuration containing environments managed by Pydantic.
    """
    return config


def get_db_manager() -> DatabaseManager:
    """
    Provide the structural database manager instance.

    Returns:
        DatabaseManager: Centralized connection and pooling orchestrator instance.
    """
    return db_manager


def get_ntfy_service(config_inst: Config = Depends(get_config_instance)) -> NtfyWebhookService:
    """
    Instantiate the notifications webhook communication channel.

    Args:
        config_inst (Config): Shared validated infrastructure environment metrics.

    Returns:
        NtfyWebhookService: Operational real-time alert messaging component.
    """
    return NtfyWebhookService(config=config_inst)


async def get_db_session(
    db_mngr: DatabaseManager = Depends(get_db_manager)
) -> AsyncGenerator[AsyncSession, None]:
    """
    Generate and manage the lifecycle of an isolated transactional database session.

    Utilizes an asynchronous generator structure to safely yield control to down-stream
    API operations and enforce strict resource disposal upon termination.

    Args:
        db_mngr (DatabaseManager): The multi-pool database engine mapping reference.

    Yields:
        AsyncGenerator[AsyncSession, None]: Active transactional pipeline targeting SQLite storage layers.
    """
    session: AsyncSession = db_mngr.get_session()
    try:
        yield session
    finally:
        await session.aclose()


def get_bcv_service(database_session: AsyncSession = Depends(get_db_session)) -> BCVService:
    """
    Inject the Banco Central de Venezuela data tracking and parsing service layer.

    Args:
        database_session (AsyncSession): Scoped transactional interface bound to the current request.

    Returns:
        BCVService: Bound functional logic matching official currency updates.
    """
    return BCVService(databasesession=database_session)


def get_binance_service(database_session: AsyncSession = Depends(get_db_session)) -> BinanceService:
    """
    Inject the Binance P2P metrics calculation and ledger extraction engine.

    Args:
        database_session (AsyncSession): Scoped transactional interface bound to the current request.

    Returns:
        BinanceService: Configured component pointing to P2P order books.
    """
    return BinanceService(databasesession=database_session)


def get_dolar_vzla_service(
    database_session: AsyncSession = Depends(get_db_session)
) -> DolarVenezuelaService:
    """
    Inject the unified synthetic market index calculator for the Venezuelan context.

    Args:
        database_session (AsyncSession): Scoped transactional interface bound to the current request.

    Returns:
        DolarVenezuelaService: Encapsulated service computing averages between parallel and official data.
    """
    return DolarVenezuelaService(database_session=database_session)


def get_fiat_exchange_service(
    database_session: AsyncSession = Depends(get_db_session)
) -> FiatExchangeService:
    """
    Inject the cross-currency fiat conversion service utilizing cross-rate calculations.

    Args:
        database_session (AsyncSession): Scoped transactional interface bound to the current request.

    Returns:
        FiatExchengeService: Active service tracking foreign pairs and exchange indices.
    """
    return FiatExchangeService(database_session=database_session)