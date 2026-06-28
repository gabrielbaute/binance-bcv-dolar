from sqlalchemy import Column, Integer, Float, DateTime, String

from app.database.base import Base

class BinanceRate(Base):
    """
    SQLAlchemy model representing historical prices for trading pairs on Binance P2P.

    This class stores the average price of an asset (e.g., USDT) against a fiat currency (e.g., VES) at a specific point in time, distinguishing between buy and sell operations. It serves as the data source for the Binance history endpoint.

    Attributes:
        id (int): Unique, auto-incremental identifier for each record.
        fiat (str): The fiat currency of the trading pair (e.g., 'VES', 'PEN', 'ARS'). This corresponds to the 'fiat' parameter in the Binance P2P API.
        asset (str): The digital asset or cryptocurrency of the pair (e.g., 'USDT', 'BTC'). Defines which asset is being quoted against the fiat currency.
        trade_type (str): The type of P2P operation. Can be 'BUY' or 'SELL'. It reflects the perspective of the user creating the advertisement.
        average_price (float): The calculated average price of active orders for the given pair and trade type at the time of the query.
        date (DateTime): The UTC timestamp when the query was performed and the average price was recorded. This is the historical record's timestamp.
    """
    __tablename__ = "binance_rates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fiat = Column(String(10), nullable=False)
    asset = Column(String(10), nullable=False)
    trade_type = Column(String(10), nullable=False)
    average_price = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)