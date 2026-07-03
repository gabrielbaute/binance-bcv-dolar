from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone

from app.enums import TradeType, FiatCurrency, BinanceAsset

class BinanceRateSQLModel(SQLModel, table=True):
    """
    SQLAlchemy model representing historical prices for trading pairs on Binance P2P.

    This class stores the average price of an asset (e.g., USDT) against a fiat currency (e.g., VES) at a specific point in time, distinguishing between buy and sell operations. It serves as the data source for the Binance history endpoint.

    Attributes:
        id (int): Unique, auto-incremental identifier for each record.
        fiat (FiatCurrency): The fiat currency of the trading pair (e.g., 'VES', 'PEN', 'ARS'). This corresponds to the 'fiat' parameter in the Binance P2P API.
        asset (BinanceAsset): The digital asset or cryptocurrency of the pair (e.g., 'USDT', 'BTC'). Defines which asset is being quoted against the fiat currency.
        trade_type (TradeType): The type of P2P operation. Can be 'BUY' or 'SELL'. It reflects the perspective of the user creating the advertisement.
        average_price (float): The calculated average price of active orders for the given pair and trade type at the time of the query.
        median_price (float): The calculated median price of active orders for the given pair and trade type at the time of the query.
        date (DateTime): The UTC timestamp when the query was performed and the average price was recorded. This is the historical record's timestamp.
    """
    __tablename__ = "binance_rates"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    fiat: FiatCurrency = Field(default=FiatCurrency.VES, nullable=False, index=True)
    asset: BinanceAsset = Field(default=BinanceAsset.USDT, nullable=False, index=True)
    trade_type: TradeType = Field(default=TradeType.BUY, nullable=False, index=True)
    average_price: float = Field(nullable=False)
    median_price: float = Field(nullable=True)
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
