from typing import List, Optional
from pydantic import BaseModel

class BinanceResponse(BaseModel):
    """
    Schema for the response from Binance P2P.

    Attributes:
        fiat (str): Fiat currency (e.g., VES, PEN).
        asset (str): Asset (USDT, BTC, etc).
        trade_type (str): Trade type (BUY or SELL).
        prices (Optional[List[float]]): List of prices. Can be empty or None if Binance returns no data.
        average_price (Optional[float]): Average price. Null if no data.
        median_price (Optional[float]): Median price. Null if no data.
    """
    fiat: str
    asset: str
    trade_type: str
    prices: Optional[List[float]] = None
    average_price: Optional[float] = None
    median_price: Optional[float] = None

    class Config:
        json_schema_extra = {
            "examples": {
                "normal_case": {
                    "summary": "Respuesta con datos",
                    "description": "Ejemplo típico con lista de precios y cálculo de media/mediana.",
                    "value": {
                        "fiat": "VES",
                        "asset": "USDT",
                        "trade_type": "BUY",
                        "prices": [345.50, 346.20, 347.00, 348.10, 349.00],
                        "average_price": 347.16,
                        "median_price": 347.00
                    }
                },
                "empty_case": {
                    "summary": "Respuesta sin datos",
                    "description": "Ejemplo cuando Binance devuelve lista vacía.",
                    "value": {
                        "fiat": "VES",
                        "asset": "USDT",
                        "trade_type": "BUY",
                        "prices": [],
                        "average_price": None,
                        "median_price": None
                    }
                }
            }
        }
