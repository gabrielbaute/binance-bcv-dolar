"""
Module defining API endpoints for official Banco Central de Venezuela (BCV) exchange rate matrices.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query

from app.enums import Currency
from app.services import BCVService
from app.api.dependencies import get_bcv_service
from app.schemas import BCVCurrencyResponse, BCVCurrencyRealTimeResponse, BCVResponse

router = APIRouter(prefix="/bcv", tags=["BCV"])

@router.get("/realtime", response_model=List[BCVCurrencyRealTimeResponse])
def realtime_bcv(bcv_service: BCVService = Depends(get_bcv_service)):
    """
    Retrieve live exchange rates matching structural parser elements for dominant assets (USD/EUR) directly from the BCV portal.
    """
    dolar = bcv_service.get_real_time_exchange_rate(Currency.DOLAR)
    euro = bcv_service.get_real_time_exchange_rate(Currency.EURO)
    return [dolar, euro]


@router.get("/dolar", response_model=Optional[BCVCurrencyResponse])
async def dolar_bcv(bcv_service: BCVService = Depends(get_bcv_service)):
    """
    Provide the daily historical dollar exchange rate synchronized inside the active ledger.
    """
    return await bcv_service.get_exchange_rate(currency=Currency.DOLAR)

@router.get("/euro", response_model=Optional[BCVCurrencyResponse])
async def euro_bcv(bcv_service: BCVService = Depends(get_bcv_service)):
    """
    Provide the daily historical euro exchange rate synchronized inside the active ledger.
    """
    return await bcv_service.get_exchange_rate(currency=Currency.EURO)

@router.get("/query", response_model=Optional[BCVCurrencyResponse])
async def query_bcv(
    currency: Currency = Query(..., description="Target currency asset supported by the tracking matrix."),
    bcv_service: BCVService = Depends(get_bcv_service),
):
    """
    Query database state blocks matching any specific official asset rate recorded on the system.
    """
    return await bcv_service.get_exchange_rate(currency)

@router.get("/all", response_model=Optional[BCVResponse])
async def get_all(
    bcv_service: BCVService = Depends(get_bcv_service)
):
    return await bcv_service.get_all_exchange_rates()