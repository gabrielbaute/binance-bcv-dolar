from typing import List, Optional
from pydantic import BaseModel

class BinanceResponse(BaseModel):
    """
    Schema for the response from Binance P2P.

    Keyword arguments:
        fiat (str): Fiat currency.
        asset (str): Asset (USDT, BTC, etc).
        trade_type (str): Trade type (BUY or SELL).
        prices (List[float]): List of prices.
        average_price (Optional[float]): Average price.
        median_price (Optional[float]): Median price.
    """
    fiat: str
    asset: str
    trade_type: str
    prices: Optional[List[float]] = None
    average_price: Optional[float] = None
    median_price: Optional[float] = None

    class Config:
        schema_extra = {
            "example": {
                "fiat": "VES",
                "asset": "USDT",
                "trade_type": "BUY",
                "prices": [345.50, 346.20, 347.00, 348.10, 349.00],
                "average_price": 347.16,
                "median_price": 347.00
            }
        }