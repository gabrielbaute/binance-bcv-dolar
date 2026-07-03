from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone

from app.enums import Currency, TradeType

class BCVRateSQLModel(SQLModel, table=True):
    """
    SQLAlchemy model representing the official exchange rates published by the BCV.

    This class stores the exchange rate for a specific foreign currency, as published by the Central Bank of Venezuela (Banco Central de Venezuela). It provides the historical data for the BCV history endpoint.

    Attributes:
        id (UUID): Unique identifier for each record.
        currency (Currency): The foreign currency to which the rate applies. It uses the currency name (e.g., 'dolar', 'euro') as defined in the `Currency` enum.
        trade_type (TradeType): The trade type for such a rate, SELL or BUY.
        rate (float): The official exchange rate of the currency in Venezuelan Bolívars (VES) for the record's date. This is the value published by the BCV.
        date (DateTime): The date (usually without a specific time, or at 00:00) to which the published exchange rate corresponds. Marks the day of the query or the official publication.
    """
    __tablename__ = "rates"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    currency: Currency = Field(default=Currency.DOLAR, nullable=False, index=True)
    trade_type: TradeType = Field(default=TradeType.SELL, nullable=False, index=True)
    rate: float = Field(nullable=False)
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False,)