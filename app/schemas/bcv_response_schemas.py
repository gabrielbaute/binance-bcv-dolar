from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.enums import Currency

class BCVCurrencyResponse(BaseModel):
    """
    Schema for the response from BCV for a single currency.

    Keyword arguments:
        currency (Currency): Currency tracked by BCV.
        rate (Optional[float]): Rate of the currency.
        date (datetime): Date of the response.
    """
    currency: Currency
    rate: Optional[float]
    date: datetime

    class Config:
        schema_extra = {
            "example": {
                "currency": "USD",
                "rate": 245.545621,
                "date": "2025-11-21T07:43:14.890702"
            }
        }

class BCVResponse(BaseModel):
    """
    Schema for the general response from BCV to all currencies.
    """
    dolar: Optional[BCVCurrencyResponse]
    euro: Optional[BCVCurrencyResponse]
    yuan: Optional[BCVCurrencyResponse]
    lira: Optional[BCVCurrencyResponse]
    rublo: Optional[BCVCurrencyResponse]

    class Config:
        schema_extra = {
            "example": {
                "dolar": {
                    "currency": "USD",
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
        }