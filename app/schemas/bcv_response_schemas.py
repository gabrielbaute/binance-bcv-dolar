from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from app.enums import Currency, TradeType

class BCVCurrencyCreate(BaseModel):
    """
    Schema for create a currency record on the database.

    Attributes:
        currency (Currency): Currency tracked by BCV.
        trade_type (TradeType): Trade type operation for the currency.
        rate (Optional[float]): Rate of the currency.
        date (datetime): Date of the response.
    """
    currency: Currency
    trade_type: TradeType
    rate: float
    date: datetime

class BCVCurrencyUpdate(BaseModel):
    """
    Schema for update a currency record on tadabase.

    Attributes:
        id (UUID): Unique identifier for the record.
        currency (Currency): Currency tracked by BCV.
        trade_type (TradeType): Trade type operation for the currency.
        rate (Optional[float]): Rate of the currency.
        date (datetime): Date of the response.
    """
    id: Optional[UUID] = None
    currency: Optional[Currency] = None
    trade_type: Optional[TradeType] = None
    rate: Optional[float] = None
    date: Optional[datetime] = None

class BCVCurrencyResponse(BaseModel):
    """
    Schema for the response from BCV for a single currency.

    Attributes:
        id (UUID): Unique identifier for the record.
        currency (Currency): Currency tracked by BCV.
        trade_type (TradeType): Trade type operation for the currency.
        rate (Optional[float]): Rate of the currency.
        date (datetime): Date of the response.
    """
    id: UUID
    currency: Currency
    trade_type: TradeType = TradeType.SELL
    rate: float
    date: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "currency": "DOLAR",
                    "trade_type": "SELL",
                    "rate": 245.545621,
                    "date": "2025-11-21T07:43:14.890702"
                }
            ]
        }
    )

class BCVCurrencyRealTimeResponse(BaseModel):
    """
    Schema for the real time response from BCV for a single currency.

    Attributes:
        currency (Currency): Currency tracked by BCV.
        trade_type (TradeType): Trade type operation for the currency.
        rate (Optional[float]): Rate of the currency.
        date (datetime): Date of the response.
    """
    currency: Currency
    trade_type: TradeType = TradeType.SELL
    rate: float
    date: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "currency": "DOLAR",
                    "rate": 245.545621,
                    "date": "2025-11-21T07:43:14.890702"
                }
            ]
        }
    )


class BCVCurrencyListResponse(BaseModel):
    """
    Schema for list response

    Attributes:
        currencies (List[BCVCurrencyResponse]): List of BCVCurrencyResponse objects
        count (int): total amount of BCVCurrencyResponse objects.
    """
    currencies: List[BCVCurrencyResponse] = []
    count: int = 0

class BCVResponse(BaseModel):
    """
    Schema for the general response from BCV to all currencies.

    Attributes:
        dolar (Optional[BCVCurrencyResponse]): BCV dolar response.
        euro (Optional[BCVCurrencyResponse]): BCV euro response.
        yuan (Optional[BCVCurrencyResponse]): BCV yuan response.
        lira (Optional[BCVCurrencyResponse]): BCV lira response.
        rublo (Optional[BCVCurrencyResponse]): BCV rublo response.
    """
    dolar: Optional[BCVCurrencyResponse]
    euro: Optional[BCVCurrencyResponse]
    yuan: Optional[BCVCurrencyResponse]
    lira: Optional[BCVCurrencyResponse]
    rublo: Optional[BCVCurrencyResponse]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "dolar": {
                        "currency": "DOLAR",
                        "rate": 245.545621,
                        "date": "2025-11-21T07:43:14.890702"
                    },
                    "euro": {
                        "currency": "EUR",
                        "rate": 260.123456,
                        "date": "2025-11-21T07:43:14.890702"
                    },
                    "yuan": {
                        "currency": "CNY",
                        "rate": 34.567890,
                        "date": "2025-11-21T07:43:14.890702"
                    },
                    "lira": {
                        "currency": "TRY",
                        "rate": 12.345678,
                        "date": "2025-11-21T07:43:14.890702"
                    },
                    "rublo": {
                        "currency": "RUB",
                        "rate": 3.456789,
                        "date": "2025-11-21T07:43:14.890702"
                    }
                }
            ]
        }
    )