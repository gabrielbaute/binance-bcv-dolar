from fastapi import APIRouter, Query

from app.services import BinanceP2P
from app.schemas import BinanceResponse

router = APIRouter(prefix="/binance", tags=["Binance"])
binance = BinanceP2P()

@router.get("/realtime_ves", response_model=BinanceResponse)
def realtime_binance_ves():
    """
    Returns the averge exchange rate in the P2P Binance market at the moment of the request.
    """
    binance = BinanceP2P()
    return binance.get_usdt_ves_pair()

@router.get("/pair", response_model=BinanceResponse, summary="Request for a specific pair in Binance P2P market")
def get_binance_pair(
    fiat: str = Query(..., description="Fiat currency, e.g. VES, PEN"),
    asset: str = Query("USDT", description="Crypto asset, default USDT"),
    trade_type: str = Query("BUY", description="Trade type: BUY or SELL")
):
    """
    Returns the P2P average exchange rate for the selected pair, and a list of the first 20 prices in the market.
    """
    return binance.get_pair(fiat=fiat, asset=asset, trade_type=trade_type, rows=20)