from fastapi import APIRouter, Query

from app.services import BinanceP2P
from app.schemas import BinanceResponse

router = APIRouter(prefix="/binance", tags=["Binance"])
binance = BinanceP2P()

@router.get("/realtime_ves", response_model=BinanceResponse)
def realtime_binance_ves():
    binance = BinanceP2P()
    return binance.get_usdt_ves_pair()

@router.get("/pair", response_model=BinanceResponse, summary="Consulta par en Binance P2P")
def get_binance_pair(
    fiat: str = Query(..., description="Fiat currency, e.g. VES, PEN"),
    asset: str = Query("USDT", description="Crypto asset, default USDT"),
    trade_type: str = Query("BUY", description="Trade type: BUY or SELL")
):
    return binance.get_pair(fiat=fiat, asset=asset, trade_type=trade_type, rows=20)