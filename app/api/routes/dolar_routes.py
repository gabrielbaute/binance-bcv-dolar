from typing import Optional
from fastapi import APIRouter, Depends

from app.services import DolarVenezuelaService
from app.api.dependencies import get_dolar_vzla_service
from app.schemas import DolarResponse, RealTimeDolarResponse

router = APIRouter(prefix="/dolar", tags=["Dolar Promedio"])

@router.get("/dolar_promedio", response_model=Optional[DolarResponse])
async def dolar_promedio(
    dolar_service: DolarVenezuelaService = Depends(get_dolar_vzla_service)
):
    """
    Returns the USD and EUR values ​​at the BCV, the USDT value on Binance P2P at the time of the query, and the average price between USD_BCV and USDT.
    """
    return await dolar_service.get_average_dolar_last_register()
    

@router.get("/realtime_dolar_promedio", response_model=RealTimeDolarResponse)
def realtime_dolar_promedio(
    dolar_service: DolarVenezuelaService = Depends(get_dolar_vzla_service)
):
    """
    Returns the USD and EUR values ​​at the BCV, the USDT value on Binance P2P at the time of the query, and the average price between USD_BCV and USDT.
    """
    return dolar_service.get_real_time_average_dolar()