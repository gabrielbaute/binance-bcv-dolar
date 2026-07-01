from typing import Tuple
from fastapi import APIRouter, Query, Depends

from app.enums import Currency
from app.services import BCVService
from app.api.dependencies import get_bcv_service
from app.schemas import (
    BCVResponse,
    BCVCurrencyResponse,
    BCVCurrencyRealTimeResponse
)

router = APIRouter(prefix="/bcv", tags=["BCV"])

@router.get("/realtime", response_model=Tuple[BCVCurrencyRealTimeResponse])
def realtime_bcv(
    bcv_service: BCVService = Depends(get_bcv_service)
):
    """
    The Euro/Dollar exchange rate for the day has been updated, according to the Central Bank of Venezuela (BCV).
    """
    dolar = bcv_service.get_real_time_exchange_rate(Currency.DOLAR)
    euro = bcv_service.get_real_time_exchange_rate(Currency.EURO)
    return dolar, euro

@router.get("/dolar", response_model=BCVCurrencyResponse)
async def dolar_bcv(
    bcv_service: BCVService = Depends(get_bcv_service)
):
    """
    It provides the daily dollar exchange rate, according to the Central Bank of Venezuela (BCV). The daily rate is set the previous day, when banks close their exchange desks and report to the BCV, which publishes the average rate at 5 pm, Venezuelan time.
    """
    return await bcv_service.get_exchange_rate(currency=Currency.DOLAR)

@router.get("/euro", response_model=BCVCurrencyResponse)
async def euro_bcv(
    bcv_service: BCVService = Depends(get_bcv_service)
):
    """
    It provides the daily euro exchange rate, according to the Central Bank of Venezuela (BCV). The daily rate is set the previous day, when banks close their exchange desks and report to the BCV, which publishes the average rate at 5 pm, Venezuelan time.
    """
    return await bcv_service.get_exchange_rate(currency=Currency.EURO)

@router.get("/query", response_model=BCVCurrencyResponse)
async def query_bcv(
    currency: str = Query(..., description="Currency to query", enum=["dolar", "euro", "yuan", "lira", "rublo"]),
    bcv_service: BCVService = Depends(get_bcv_service)
    ):
    """
    Returns the average echange rate for the day for the selected currency.
    """
    enum_currency = Currency.map_currency(currency)
    return await bcv_service.get_exchange_rate(enum_currency)

@router.get("/all", response_model=BCVResponse)
async def get_real_time_all(
    bcv_service: BCVService = Depends(get_bcv_service)
):
    return await bcv_service.get_all_exchange_rates()