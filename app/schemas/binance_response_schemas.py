from typing import List, Optional, Any
from pydantic import BaseModel

class TradeMethod(BaseModel):
    payType: str
    identifier: str
    tradeMethodName: Optional[str]
    tradeMethodShortName: Optional[str]

class Adv(BaseModel):
    advNo: str
    tradeType: str
    asset: str
    fiatUnit: str
    price: str
    surplusAmount: Optional[str]
    tradableQuantity: Optional[str]
    minSingleTransAmount: Optional[str]
    maxSingleTransAmount: Optional[str]
    tradeMethods: List[TradeMethod]
    isTradable: bool

class Advertiser(BaseModel):
    nickName: str
    monthOrderCount: Optional[int]
    monthFinishRate: Optional[float]
    positiveRate: Optional[float]
    userType: str

class DataItem(BaseModel):
    adv: Adv
    advertiser: Advertiser

class BinanceResponse(BaseModel):
    code: str
    message: Optional[str]
    messageDetail: Optional[str]
    data: List[DataItem]
    total: Optional[int]
    success: bool
