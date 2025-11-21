from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.enums import Currency

class BCVCurrencyResponse(BaseModel):
    """
    Schema for the response from BCV for a single currency.

    Keyword arguments:
        currency (Currency): Currency.
        rate (Optional[float]): Rate of the currency.
        date (datetime): Date of the response.
    """
    currency: Currency
    rate: Optional[float]
    date: datetime

class BCVResponse(BaseModel):
    """
    Schema for the general response from BCV to all currencies.
    """
    dolar: Optional[BCVCurrencyResponse]
    euro: Optional[BCVCurrencyResponse]
    yuan: Optional[BCVCurrencyResponse]
    lira: Optional[BCVCurrencyResponse]
    rublo: Optional[BCVCurrencyResponse]