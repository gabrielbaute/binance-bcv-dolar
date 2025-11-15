from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.schemas.bcv_response_schema import BCVCurrencyResponse
from app.schemas.binance_response_schemas import BinanceResponse

class DolarResponse(BaseModel):
    """
    Schema for dolar prices from BCV and Binance.

    Keyword arguments:
        bcv (Optional[BCVCurrencyResponse]): BCV response.
        binance (Optional[BinanceResponse]): Binance response.
        average (Optional[float]): Average price between BCV and Binance.
        date (datetime): Date of the response.
    """
    bcv: Optional[BCVCurrencyResponse]
    binance: Optional[BinanceResponse]
    average: Optional[float]
    date: datetime