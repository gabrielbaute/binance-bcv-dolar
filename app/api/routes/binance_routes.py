from fastapi import APIRouter

from app.services import BinanceP2P
from app.schemas import BinanceResponse

router = APIRouter(prefix="/binance", tags=["Binance"])

@router.get("/realtime", response_model=BinanceResponse)
def realtime_binance():
    binance = BinanceP2P()
    return binance.get_usdt_ves_pair()
