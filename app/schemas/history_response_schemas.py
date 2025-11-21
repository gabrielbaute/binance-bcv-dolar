from datetime import datetime
from typing import List
from pydantic import BaseModel

class BCVHistoryItem(BaseModel):
    id: int
    currency: str
    rate: float
    date: datetime

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "currency": "USD",
                "rate": 40.25,
                "date": "2025-11-21T00:00:00"
            }
        }

class BinanceHistoryItem(BaseModel):
    id: int
    fiat: str
    asset: str
    trade_type: str
    average_price: float
    date: datetime

    class Config:
        schema_extra = {
            "example": {
                "id": 10,
                "fiat": "VES",
                "asset": "USDT",
                "trade_type": "BUY",
                "average_price": 346.97,
                "date": "2025-11-21T09:00:00"
            }
        }

class BCVHistoryResponse(BaseModel):
    history: List[BCVHistoryItem]

class BinanceHistoryResponse(BaseModel):
    history: List[BinanceHistoryItem]
