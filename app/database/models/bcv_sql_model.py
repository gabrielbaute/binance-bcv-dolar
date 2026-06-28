from sqlalchemy import Column, Integer, Float, DateTime, String

from app.database.base import Base

class BCVRate(Base):
    """
    SQLAlchemy model representing the official exchange rates published by the BCV.

    This class stores the exchange rate for a specific foreign currency, as published by the Central Bank of Venezuela (Banco Central de Venezuela). It provides the historical data for the BCV history endpoint.

    Attributes:
        id (int): Unique, auto-incremental identifier for each record.
        currency (str): The foreign currency to which the rate applies. It uses the currency name (e.g., 'dolar', 'euro') as defined in the `Currency` enum.
        rate (float): The official exchange rate of the currency in Venezuelan Bolívars (VES) for the record's date. This is the value published by the BCV.
        date (DateTime): The date (usually without a specific time, or at 00:00) to which the published exchange rate corresponds. Marks the day of the query or the official publication.
    """
    __tablename__ = "bcv_rates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency = Column(String(10), nullable=False)
    rate = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)