from typing import List, Optional, Any
from pydantic import BaseModel

class BinanceRequest(BaseModel):
    fiat: str
    page: int = 1
    rows: int = 20
    tradeType: str
    asset: str
    countries: List[str] = []
    proMerchantAds: bool = False
    shieldMerchantAds: bool = False
    filterType: str = "tradable"
    periods: List[Any] = []
    additionalKycVerifyFilter: int = 0
    publisherType: Optional[str] = None
    payTypes: List[str] = []
    classifies: List[str] = ["mass", "profession", "fiat_trade"]
    tradedWith: bool = False
    followed: bool = False