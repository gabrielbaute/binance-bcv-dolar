from fastapi import APIRouter

from app.services import DolarService
from app.schemas import DolarResponse

router = APIRouter(prefix="/dolar", tags=["Dolar Promedio"])
@router.get("/venezuela", response_model=DolarResponse)
def venezuela_dolar():
    """
    Returns the USD and EUR values ​​at the BCV, the USDT value on Binance P2P at the time of the query, and the average price between USD_BCV and USDT.
    """
    service = DolarService()
    return service.get_average_dolar()