from typing import List, Optional, Any
from pydantic import BaseModel

class BinanceRequest(BaseModel):
    """
    Schema for the request to Binance P2P.

    Keyword arguments:
        fiat (str): Fiat currency.
        page (int): Page number.
        rows (int): Number of rows per page.
        tradeType (str): Trade type.
        asset (str): Asset (USDT, BTC, etc).
        countries (List[str]): List of countries.
        proMerchantAds (bool): Pro merchant ads.
        shieldMerchantAds (bool): Shield merchant ads.
        filterType (str): Filter type.
        periods (List[Any]): Periods.
        additionalKycVerifyFilter (int): Additional KYC verify filter.
        publisherType (Optional[str]): Publisher type.
        payTypes (List[str]): List of pay types.
        classifies (List[str]): List of classifies.
        tradedWith (bool): Traded with.
    """
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