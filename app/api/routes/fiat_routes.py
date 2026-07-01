from fastapi import APIRouter, Query, Depends

from app.enums import FiatCurrency
from app.services import FiatExchengeService
from app.api.dependencies import get_fiat_exchenge_service
from app.schemas.fiats_pair_response import FiatPairResponse

router = APIRouter(prefix="/arbitrage", tags=["Remesas/Arbitraje"])

@router.get("/pair", response_model=FiatPairResponse, summary="Get fiat/fiat pair from last database record.")
async def get_fiat_pair(
    fiat_1: str = Query(..., description="First fiat currency, e.g. VES"),
    fiat_2: str = Query(..., description="Second fiat currency, e.g. PEN"),
    exchenge_service: FiatExchengeService = Depends(get_fiat_exchenge_service)
):
    """
    Returns the average exchange rate for the selected pair. This route is used to calculate estimated remittance prices. It requires the currency of both countries and calculates rates in both directions.
    """
    fiat_1_value = FiatCurrency.from_string(fiat_1)
    fiat_2_value = FiatCurrency.from_string(fiat_2)
    return await exchenge_service.get_pair(fiat_1_value, fiat_2_value)

@router.get("/real_time_pair", response_model=FiatPairResponse, summary="Get fiat/fiat pair fetching prices direct from Binance.")
def get_real_time_pair(
    fiat_1: str = Query(..., description="First fiat currency, e.g. VES"),
    fiat_2: str = Query(..., description="Second fiat currency, e.g. PEN"),
    exchenge_service: FiatExchengeService = Depends(get_fiat_exchenge_service)   
):
    """
    Returns the average exchange rate for the selected pair. No database query, fetch direct from Binance and calculate rates.
    """
    fiat_1_value = FiatCurrency.from_string(fiat_1)
    fiat_2_value = FiatCurrency.from_string(fiat_2)
    return exchenge_service.get_real_time_pair(fiat_1_value, fiat_2_value)