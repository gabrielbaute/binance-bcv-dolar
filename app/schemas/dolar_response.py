from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.schemas.bcv_response_schemas import BCVCurrencyResponse, BCVCurrencyRealTimeResponse
from app.schemas.binance_response_schemas import BinanceCurrencyResponse, BinanceRealTimeResponse

class RealTimeDolarResponse(BaseModel):
    """
    Schema for dolar prices from BCV and Binance for Venezuela interest case.

    Attributes:
        bcv_dolar (Optional[BCVCurrencyRealTimeResponse]): BCV dolar response.
        bcv_euro (Optional[BCVCurrencyRealTimeResponse]): BCV euro response.
        binance_usdt_ves_buy (Optional[BinanceRealTimeResponse]): Binance USDT/VES response at Buy trade type.
        average_usdt_ves (Optional[float]): Average price between BCV and Binance.
        date (datetime): Date of the response.
    """
    bcv_dolar: Optional[BCVCurrencyRealTimeResponse]
    bcv_euro: Optional[BCVCurrencyRealTimeResponse]
    binance_usdt_ves_buy: Optional[BinanceRealTimeResponse]
    average_usdt_ves: Optional[float]
    date: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
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
            ]
        }
    )

class DolarResponse(BaseModel):
    """
    Schema for dolar prices from BCV and Binance for Venezuela interest case.

    Attributes:
        bcv_dolar (Optional[BCVCurrencyResponse]): BCV dolar response.
        bcv_euro (Optional[BCVCurrencyResponse]): BCV euro response.
        binance_usdt_ves_buy (Optional[BinanceCurrencyResponse]): Binance USDT/VES response at Buy trade type.
        average_usdt_ves (Optional[float]): Average price between BCV and Binance.
        date (datetime): Date of the response.
    """
    bcv_dolar: Optional[BCVCurrencyResponse]
    bcv_euro: Optional[BCVCurrencyResponse]
    binance_usdt_ves_buy: Optional[BinanceCurrencyResponse]
    average_usdt_ves: Optional[float]
    date: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "bcv_dolar": {
                        "id": "sdf-1234-5678-9012",
                        "currency": "USD",
                        "rate": 245.54,
                        "date": "2025-11-21T00:00:00"
                    },
                    "bcv_euro": {
                        "id": "sdf-1234-5678-9012",
                        "currency": "EUR",
                        "rate": 260.12,
                        "date": "2025-11-21T00:00:00"
                    },
                    "binance_usdt_ves_buy": {
                        "id": "sdf-1234-5678-9012",
                        "fiat": "VES",
                        "asset": "USDT",
                        "trade_type": "BUY",
                        "average_price": 346.97,
                        "date": "2025-11-21T09:00:00"
                    },
                    "average_usdt_ves": 296.25,
                    "date": "2025-11-21T09:00:00"
                }
            ]
        }
    )