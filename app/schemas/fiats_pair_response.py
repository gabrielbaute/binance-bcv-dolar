from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.schemas.binance_response_schemas import BinanceResponse

class FiatPairResponse(BaseModel):
    """
    Schema for fiat pair prices from Binance.

    Attributes:
        fiat_1_p2p_buy (Optional[BinanceResponse]): Fiat 1 P2P response for buy.
        fiat_1_p2p_sell (Optional[BinanceResponse]): Fiat 1 P2P response for sell.
        fiat_2_p2p_buy (Optional[BinanceResponse]): Fiat 2 P2P response for buy.
        fiat_2_p2p_sell (Optional[BinanceResponse]): Fiat 2 P2P response for sell.
        average_exchange_rate_f1_f2 (Optional[float]): Exchange rate from Fiat 1 to Fiat 2.
        average_exchange_rate_f2_f1 (Optional[float]): Exchange rate from Fiat 2 to Fiat 1.
        date (datetime): Date of the response.
    """
    fiat_1_p2p_buy: Optional[BinanceResponse]
    fiat_1_p2p_sell: Optional[BinanceResponse]
    fiat_2_p2p_buy: Optional[BinanceResponse]
    fiat_2_p2p_sell: Optional[BinanceResponse]
    average_exchange_rate_f1_f2: Optional[float]
    average_exchange_rate_f2_f1: Optional[float]
    date: datetime

    class Config:
        schema_extra = {
            "examples": {
                "normal_case": {
                    "summary": "Respuesta con datos",
                    "description": "Ejemplo típico con datos completos para VES/PEN.",
                    "value": {
                        "fiat_1_p2p_buy": {
                            "fiat": "VES",
                            "asset": "USDT",
                            "trade_type": "BUY",
                            "prices": [345.50, 346.20, 347.00],
                            "average_price": 346.23,
                            "median_price": 346.20
                        },
                        "fiat_1_p2p_sell": {
                            "fiat": "VES",
                            "asset": "USDT",
                            "trade_type": "SELL",
                            "prices": [344.00, 344.50, 345.00],
                            "average_price": 344.50,
                            "median_price": 344.50
                        },
                        "fiat_2_p2p_buy": {
                            "fiat": "PEN",
                            "asset": "USDT",
                            "trade_type": "BUY",
                            "prices": [3.75, 3.76, 3.77],
                            "average_price": 3.76,
                            "median_price": 3.76
                        },
                        "fiat_2_p2p_sell": {
                            "fiat": "PEN",
                            "asset": "USDT",
                            "trade_type": "SELL",
                            "prices": [3.74, 3.75, 3.76],
                            "average_price": 3.75,
                            "median_price": 3.75
                        },
                        "average_exchange_rate_f1_f2": 0.0108,
                        "average_exchange_rate_f2_f1": 92.266,
                        "date": "2025-11-21T09:00:00"
                    }
                },
                "empty_case": {
                    "summary": "Respuesta con datos faltantes",
                    "description": "Ejemplo cuando uno de los pares devuelve lista vacía.",
                    "value": {
                        "fiat_1_p2p_buy": {
                            "fiat": "VES",
                            "asset": "USDT",
                            "trade_type": "BUY",
                            "prices": [],
                            "average_price": None,
                            "median_price": None
                        },
                        "fiat_1_p2p_sell": {
                            "fiat": "VES",
                            "asset": "USDT",
                            "trade_type": "SELL",
                            "prices": [],
                            "average_price": None,
                            "median_price": None
                        },
                        "fiat_2_p2p_buy": {
                            "fiat": "PEN",
                            "asset": "USDT",
                            "trade_type": "BUY",
                            "prices": [3.75, 3.76, 3.77],
                            "average_price": 3.76,
                            "median_price": 3.76
                        },
                        "fiat_2_p2p_sell": {
                            "fiat": "PEN",
                            "asset": "USDT",
                            "trade_type": "SELL",
                            "prices": [3.74, 3.75, 3.76],
                            "average_price": 3.75,
                            "median_price": 3.75
                        },
                        "average_exchange_rate_f1_f2": None,
                        "average_exchange_rate_f2_f1": None,
                        "date": "2025-11-21T09:00:00"
                    }
                }
            }
        }
