"""
Module defining API endpoints for cross-currency fiat exchange and remittance arbitrage calculations.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query

from app.enums import FiatCurrency
from app.services import FiatExchangeService
from app.api.dependencies import get_fiat_exchange_service
from app.schemas.fiats_pair_response import FiatPairResponse

router = APIRouter(prefix="/arbitrage", tags=["Remesas/Arbitraje"])


@router.get("/pair", response_model=Optional[FiatPairResponse], summary="Get fiat/fiat pair from last database record.")
async def get_fiat_pair(
    fiat_1: FiatCurrency = Query(..., description="First local fiat currency tracking asset."),
    fiat_2: FiatCurrency = Query(..., description="Second local fiat currency tracking asset."),
    exchange_service: FiatExchangeService = Depends(get_fiat_exchange_service),
):
    """
    Returns the average exchange rate for the selected pair based on stored operational database blocks.
    
    This route evaluates metrics used to estimate remittance conversions across both directions.
    """
    return await exchange_service.get_pair(fiat_1, fiat_2)


@router.get("/real_time_pair", response_model=FiatPairResponse, summary="Get fiat/fiat pair fetching prices direct from Binance.")
async def get_real_time_pair(
    fiat_1: FiatCurrency = Query(..., description="First local fiat currency tracking asset."),
    fiat_2: FiatCurrency = Query(..., description="Second local fiat currency tracking asset."),
    exchange_service: FiatExchangeService = Depends(get_fiat_exchange_service),
):
    """
    Returns the dynamic live pricing metrics for the selected fiat assets mapping order books directly.
    """
    return exchange_service.get_real_time_pair(fiat_1, fiat_2)