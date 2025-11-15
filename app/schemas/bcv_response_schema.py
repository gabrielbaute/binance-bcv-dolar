from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.enums import Currency

class BCVCurrencyResponse(BaseModel):
    """Schema for the response from BCV for a single currency."""
    currency: Currency
    rate: Optional[float]
    date: datetime

class BCVResponse(BaseModel):
    """Schema for the general response from BCV to all currencies."""
    dolar: Optional[BCVCurrencyResponse]
    euro: Optional[BCVCurrencyResponse]
    yuan: Optional[BCVCurrencyResponse]
    lira: Optional[BCVCurrencyResponse]
    rublo: Optional[BCVCurrencyResponse]