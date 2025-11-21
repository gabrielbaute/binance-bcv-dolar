from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.schemas.bcv_response_schemas import BCVCurrencyResponse
from app.schemas.binance_response_schemas import BinanceResponse
from app.enums import Currency

class DolarResponse(BaseModel):
    """
    Schema for dolar prices from BCV and Binance for Venezuela interest case.

    Keyword arguments:
        bcv_dolar (Optional[BCVCurrencyResponse]): BCV dolar response.
        bcv_euro (Optional[BCVCurrencyResponse]): BCV euro response.
        binance_usdt_ves_buy (Optional[BinanceResponse]): Binance USDT/VES response at Buy trade type.
        average_usdt_ves (Optional[float]): Average price between BCV and Binance.
        date (datetime): Date of the response.
    """
    bcv_dolar: Optional[BCVCurrencyResponse]
    bcv_euro: Optional[BCVCurrencyResponse]
    binance_usdt_ves_buy: Optional[BinanceResponse]
    average_usdt_ves: Optional[float]
    date: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "bcv_dolar": {
                    "currency": "USD",
                    "rate": 245.54,
                    "date": "2025-11-21T00:00:00"
                },
                "bcv_euro": {
                    "currency": "EUR",
                    "rate": 260.12,
                    "date": "2025-11-21T00:00:00"
                },
                "binance_usdt_ves_buy": {
                    "fiat": "VES",
                    "asset": "USDT",
                    "trade_type": "BUY",
                    "average_price": 346.97,
                    "date": "2025-11-21T09:00:00"
                },
                "average_usdt_ves": 296.25,
                "date": "2025-11-21T09:00:00"
            }
        }