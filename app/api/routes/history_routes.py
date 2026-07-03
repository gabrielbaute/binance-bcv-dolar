"""
Module defining API endpoints for historical rate queries (BCV, Binance, and fiat cross-pairs).
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query

from app.enums import Currency, FiatCurrency, BinanceAsset, TradeType
from app.services import BCVService, BinanceService, FiatExchangeService
from app.api.dependencies import get_bcv_service, get_binance_service, get_fiat_exchange_service
from app.schemas import (
    BCVCurrencyListResponse,
    BinanceCurrencyListResponse,
)
from app.schemas.fiats_pair_response import FiatPairResponse

router = APIRouter(prefix="/history", tags=["History"])


# ─────────────────────────────────────────────
# BCV History
# ─────────────────────────────────────────────

@router.get(
    "/bcv",
    response_model=BCVCurrencyListResponse,
    summary="Historical BCV rates by currency and date range",
)
async def history_bcv(
    currency: Currency = Query(Currency.DOLAR, description="Currency to consult (DOLAR, EURO, YUAN, LIRA, RUBLE)."),
    trade_type: TradeType = Query(TradeType.SELL, description="Trade type (BUY, SELL)."),
    start_date: Optional[datetime] = Query(None, description="Start date (YYYY-MM-DDTHH:MM:SS)."),
    end_date: Optional[datetime] = Query(None, description="End date (YYYY-MM-DDTHH:MM:SS)."),
    skip: int = Query(0, ge=0, description="Records to skip (pagination)."),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return."),
    bcv_service: BCVService = Depends(get_bcv_service),
) -> None:
    """Return historical official BCV rates for a specific currency, with optional date range filter."""
    if start_date and end_date:
        return await bcv_service.get_currency_exchange_rates_by_range(
            currency=currency,
            trade_type=trade_type,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit,
        )
    return await bcv_service.get_all_currency_registers(
        currency=currency,
        trade_type=trade_type,
        skip=skip,
        limit=limit,
    )


# ─────────────────────────────────────────────
# Binance History
# ─────────────────────────────────────────────

@router.get(
    "/binance",
    response_model=BinanceCurrencyListResponse,
    summary="Historical Binance P2P rates by pair and date range",
)
async def history_binance(
    fiat: FiatCurrency = Query(FiatCurrency.VES, description="Fiat currency (VES, PEN, COP, etc.)."),
    asset: BinanceAsset = Query(BinanceAsset.USDT, description="Crypto asset (USDT, BTC, etc.)."),
    trade_type: TradeType = Query(TradeType.BUY, description="Trade type (BUY, SELL)."),
    start_date: Optional[datetime] = Query(None, description="Start date (YYYY-MM-DDTHH:MM:SS)."),
    end_date: Optional[datetime] = Query(None, description="End date (YYYY-MM-DDTHH:MM:SS)."),
    skip: int = Query(0, ge=0, description="Records to skip (pagination)."),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return."),
    binance_service: BinanceService = Depends(get_binance_service),
) -> None:
    """Return historical Binance P2P rates for a specific pair (fiat/asset), with optional date range filter."""
    if start_date and end_date:
        return await binance_service.get_binance_pair_by_time_range(
            fiat=fiat,
            asset=asset,
            trade_type=trade_type,
            start_time=start_date,
            end_time=end_date,
            skip=skip,
            limit=limit,
        )
    return await binance_service.get_all_saved_binance_pair(
        fiat=fiat,
        asset=asset,
        trade_type=trade_type,
        skip=skip,
        limit=limit,
    )


# ─────────────────────────────────────────────
# Fiat Cross-Pair History  (experimental)
# ─────────────────────────────────────────────

@router.get(
    "/fiat-pair",
    response_model=list[FiatPairResponse],
    summary="[Experimental] Historical cross fiat pair rates (VES→PEN, etc.)",
)
async def history_fiat_pair(
    fiat_1: FiatCurrency = Query(..., description="Source fiat currency."),
    fiat_2: FiatCurrency = Query(..., description="Destination fiat currency."),
    start_date: datetime = Query(..., description="Start date (YYYY-MM-DDTHH:MM:SS)."),
    end_date: datetime = Query(..., description="End date (YYYY-MM-DDTHH:MM:SS)."),
    skip: int = Query(0, ge=0, description="Records to skip (pagination)."),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return."),
    exchange_service: FiatExchangeService = Depends(get_fiat_exchange_service),
) -> None:
    """
    [Experimental] Return historical cross-exchange rates between two fiat currencies calculated from Binance P2P records.

    **WARNING**: This endpoint uses the `get_historical_pair` method from `FiatExchangeService` which has not been thoroughly tested yet. Results may be inaccurate or require adjustments.
    """
    return await exchange_service.get_historical_pair(
        fiat_1=fiat_1,
        fiat_2=fiat_2,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )
