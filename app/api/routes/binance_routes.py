from typing import Tuple
from fastapi import APIRouter, Query, Depends

from app.services import BinanceService
from app.api.dependencies import get_binance_service
from app.enums import FiatCurrency, BinanceAsset, TradeType
from app.schemas import (
    BinanceRealTimeResponse,
    BinanceCurrencyResponse,
)

router = APIRouter(prefix="/binance", tags=["Binance"])

@router.get("/realtime_ves", response_model=BinanceRealTimeResponse)
def realtime_binance_ves(
    binance_service: BinanceService = Depends(get_binance_service)
):
    """
    Returns the averge exchange rate in the P2P Binance market at the moment of the request.
    """
    return binance_service.get_real_time_usdt_ves_pair()

@router.get("/real_time_pair", response_model=BinanceRealTimeResponse, summary="Request for a specific pair in Binance P2P market")
def get_binance_pair(
    fiat: str = Query(..., description="Fiat currency, e.g. VES, PEN"),
    asset: str = Query("USDT", description="Crypto asset, default USDT"),
    trade_type: str = Query("BUY", description="Trade type: BUY or SELL"),
    binance_service: BinanceService = Depends(get_binance_service)
):
    """
    Returns the P2P average exchange rate for the selected pair, and a list of the first 20 prices in the market.
    """
    fiat_value = FiatCurrency.from_string(fiat)
    asset_value = BinanceAsset.from_string(asset)
    trade_type_value = TradeType.from_string(trade_type)
    pair = binance_service.get_real_time_pair(
        fiat=fiat_value,
        asset=asset_value,
        trade_type=trade_type_value,
        rows=20
    )
    return pair

@router.get("/ves_usdt_pair", response_model=Tuple[BinanceCurrencyResponse])
async def get_ves_usdt_pair(
    binance_service: BinanceService = Depends(get_binance_service)
):
    """
    Returns de VES/USDT pair in BUY and SELL trade type from the last register of the database.
    """
    sell_price = await binance_service.get_last_saved_binance_fiat(
        fiat=FiatCurrency.VES,
        asset=BinanceAsset.USDT,
        trade_type=TradeType.SELL
    )
    buy_price = await binance_service.get_last_saved_binance_fiat(
        fiat=FiatCurrency.VES,
        asset=BinanceAsset.USDT,
        trade_type=TradeType.BUY
    )
    return sell_price, buy_price

@router.get("/pairs_last_record", response_model=Tuple[BinanceCurrencyResponse])
async def get_pairs_last_record(
    fiat: str = Query(..., description="Fiat currency, e.g. VES, PEN"),
    asset: str = Query("USDT", description="Crypto asset, default USDT"),
    binance_service: BinanceService = Depends(get_binance_service)
):
    """
    Returns the last record of a given pair
    """
    fiat_value = FiatCurrency.from_string(fiat)
    asset_value = BinanceAsset.from_string(asset)
    sell_price = await binance_service.get_last_saved_binance_fiat(fiat_value, asset_value, TradeType.SELL)
    buy_price = await binance_service.get_last_saved_binance_fiat(fiat_value, asset_value, TradeType.BUY)
    return sell_price, buy_price