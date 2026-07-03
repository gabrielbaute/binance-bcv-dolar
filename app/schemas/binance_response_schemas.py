"""
Pydantic schemas for Binance P2P market rate data validation and serialization.
"""
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.enums import TradeType, BinanceAsset, FiatCurrency

class BinanceRealTimeResponse(BaseModel):
    """
    Schema for the response from Binance P2P.

    Attributes:
        fiat (FiatCurrency): Fiat currency (e.g., VES, PEN).
        asset (BinanceAsset): Asset (USDT, BTC, etc).
        trade_type (TradeType): Trade type (BUY or SELL).
        prices (Optional[List[float]]): List of prices. Can be empty or None if Binance returns no data.
        average_price (Optional[float]): Average price. Null if no data.
        median_price (Optional[float]): Median price. Null if no data.
    """
    fiat: FiatCurrency
    asset: BinanceAsset
    trade_type: TradeType
    prices: Optional[List[float]] = None
    average_price: Optional[float] = None
    median_price: Optional[float] = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "fiat": "VES",
                    "asset": "USDT",
                    "trade_type": "BUY",
                    "prices": [345.50, 346.20, 347.00, 348.10, 349.00],
                    "average_price": 347.16,
                    "median_price": 347.00
                },
                {
                    "fiat": "VES",
                    "asset": "USDT",
                    "trade_type": "BUY",
                    "prices": [],
                    "average_price": None,
                    "median_price": None
                }
            ]
        }
    )

class BinanceCurrencyCreate(BaseModel):
    """
    Schema representing validation rules for recording a new Binance P2P statistical rate.

    This model is used to validate incoming payloads when the scraping service or an internal task registers calculated price metrics for a specific trading pair.

    Attributes:
        fiat (FiatCurrency): The fiat currency target used in the P2P market query.
        asset (BinanceAsset): The digital asset stablecoin cryptocurrency being quoted.
        trade_type (TradeType): The P2P book perspective, representing BUY or SELL orders.
        average_price (float): The calculated average price of top active orders.
        median_price (float): The calculated median price of top active orders.
    """

    fiat: FiatCurrency = Field(default=FiatCurrency.VES, description="The fiat currency of the trading pair used in the P2P market query.")
    asset: BinanceAsset = Field(default=BinanceAsset.USDT, description="The digital asset or stablecoin cryptocurrency being quoted.")
    trade_type: TradeType = Field(default=TradeType.BUY, description="The P2P operation perspective, representing either BUY or SELL order books.")
    average_price: float = Field(..., gt=0, description="The calculated average price of the top active orders at execution time.")
    median_price: float = Field(..., gt=0, description="The calculated median price of the top active orders at execution time.")


class BinanceCurrencyUpdate(BaseModel):
    """
    Schema for updating an existing tracked Binance P2P market record.

    All fields are optional, enabling partial updates (PATCH operations) over historical statistical records.

    Attributes:
        fiat (Optional[FiatCurrency]): Updated fiat currency targeting.
        asset (Optional[BinanceAsset]): Updated cryptocurrency token targeting.
        trade_type (Optional[TradeType]): Updated order book perspective constraint.
        average_price (Optional[float]): Updated calculated average price value.
        median_price (Optional[float]): Updated calculated median price value.
    """

    fiat: Optional[FiatCurrency] = Field(default=None, description="Updated fiat currency targeting.")
    asset: Optional[BinanceAsset] = Field(default=None, description="Updated cryptocurrency token targeting.")
    trade_type: Optional[TradeType] = Field(default=None, description="Updated order book perspective constraint.")
    average_price: Optional[float] = Field(default=None, gt=0, description="Updated calculated average price value.")
    median_price: Optional[float] = Field(default=None, gt=0, description="Updated calculated median price value.")

class BinanceCurrencyResponse(BaseModel):
    """
    Serialization model representing data layout output parsed to the clients.

    This schema includes database-generated tracking fields like 'id' and 'date' and structures the individual exchange rate records returned by the endpoints.

    Attributes:
        id (UUID): Unique database auto-generated record token identifier.
        fiat (FiatCurrency): The fiat currency target recorded for the trading pair.
        asset (BinanceAsset): The digital asset stablecoin cryptocurrency recorded.
        trade_type (TradeType): The P2P book perspective recorded (BUY or SELL).
        average_price (float): The persistent calculated historical average price.
        median_price (float): The persistent calculated historical median price.
        date (datetime): The UTC timestamp when the metrics were written to the database.
    """

    id: UUID = Field(..., description="Unique database auto-generated record token identifier.")
    fiat: FiatCurrency = Field(..., description="The fiat currency of the trading pair used in the P2P market query.")
    asset: BinanceAsset = Field(..., description="The digital asset or stablecoin cryptocurrency being quoted.")
    trade_type: TradeType = Field(..., description="The P2P operation perspective, representing either BUY or SELL order books.")
    average_price: Optional[float] = Field(..., gt=0, description="The calculated average price of the top active orders at execution time.")
    median_price: Optional[float] = Field(..., gt=0, description="The calculated median price of the top active orders at execution time.")
    date: datetime = Field(..., description="The UTC timestamp when the query metrics were written to the database.")

    model_config = ConfigDict(from_attributes=True)


class BinanceCurrencyListResponse(BaseModel):
    """
    Paginated collection payload structure aggregating multiple rate response items.

    This layout ensures clients receive consistency concerning pagination states, binding both the requested records window slice and the real overall table records total.

    Attributes:
        currencies (List[BinanceCurrencyResponse]): Collection list containing validated rate objects.
        count (int): Absolute global count matching filters to manage client pagination.
    """
    currencies: List[BinanceCurrencyResponse] = Field(..., description="Collection list containing validated rate dataset representations.")
    count: int = Field(..., ge=0, description="Absolute global count matching filters used to manage client pagination states.")

    model_config = ConfigDict(from_attributes=True)