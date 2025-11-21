from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict

class BCVHistoryItem(BaseModel):
    """
    Schema for a single historical BCV record.

    Attributes:
        id (int): Database ID of the record.
        currency (str): Currency symbol (e.g., USD, EUR).
        rate (float): Exchange rate value.
        date (datetime): Timestamp of the record.
    """
    id: int
    currency: str
    rate: float
    date: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "currency": "USD",
                    "rate": 40.25,
                    "date": "2025-11-21T00:00:00"
                }
            ]
        }
    )

class BinanceHistoryItem(BaseModel):
    """
    Schema for a single historical Binance P2P record.

    Attributes:
        id (int): Database ID of the record.
        fiat (str): Fiat currency (e.g., VES).
        asset (str): Crypto asset (e.g., USDT).
        trade_type (str): Type of trade (BUY/SELL).
        average_price (float): Calculated average price.
        date (datetime): Timestamp of the record.
    """
    id: int
    fiat: str
    asset: str
    trade_type: str
    average_price: float
    date: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 10,
                    "fiat": "VES",
                    "asset": "USDT",
                    "trade_type": "BUY",
                    "average_price": 346.97,
                    "date": "2025-11-21T09:00:00"
                }
            ]
        }
    )

class BCVHistoryResponse(BaseModel):
    """
    Schema for a list of historical BCV records.

    Attributes:
        history (List[BCVHistoryItem]): List of historical items.
    """
    history: List[BCVHistoryItem]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "history": [
                        {
                            "id": 1,
                            "currency": "USD",
                            "rate": 40.25,
                            "date": "2025-11-21T00:00:00"
                        },
                        {
                            "id": 2,
                            "currency": "EUR",
                            "rate": 42.50,
                            "date": "2025-11-21T00:00:00"
                        }
                    ]
                }
            ]
        }
    )

class BinanceHistoryResponse(BaseModel):
    """
    Schema for a list of historical Binance records.

    Attributes:
        history (List[BinanceHistoryItem]): List of historical items.
    """
    history: List[BinanceHistoryItem]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "history": [
                        {
                            "id": 10,
                            "fiat": "VES",
                            "asset": "USDT",
                            "trade_type": "BUY",
                            "average_price": 346.97,
                            "date": "2025-11-21T09:00:00"
                        },
                        {
                            "id": 11,
                            "fiat": "VES",
                            "asset": "USDT",
                            "trade_type": "SELL",
                            "average_price": 345.50,
                            "date": "2025-11-21T09:05:00"
                        }
                    ]
                }
            ]
        }
    )