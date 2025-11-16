from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.schemas.binance_response_schemas import BinanceResponse

class FiatPairResponse(BaseModel):
    """
    Schema for fiat pair prices from Binance.

    Keyword arguments:
        fiat_1_p2p_buy (Optional[BinanceResponse]): Fiat 1 P2P response for buy.
        fiat_1_p2p_sell (Optional[BinanceResponse]): Fiat 1 P2P response for sell
        fiat_2_p2p_buy (Optional[BinanceResponse]): Fiat 2 P2P response for buy.
        fiat_2_p2p_sell (Optional[BinanceResponse]): Fiat 2 P2P response for sell
        average_exchange_rate_f1_f2 (Optional[float]): Average exchange rate from Fiat 1 to Fiat 2.
        average_exchange_rate_f2_f1 (Optional[float]): Average exchange rate from Fiat 2 to Fiat 1.
        date (datetime): Date of the response.
    """
    fiat_1_p2p_buy: Optional[BinanceResponse]
    fiat_1_p2p_sell: Optional[BinanceResponse]
    fiat_2_p2p_buy: Optional[BinanceResponse]
    fiat_2_p2p_sell: Optional[BinanceResponse]
    average_exchange_rate_f1_f2: Optional[float]
    average_exchange_rate_f2_f1: Optional[float]
    date: datetime