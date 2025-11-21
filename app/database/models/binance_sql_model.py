from sqlalchemy import Column, Integer, Float, DateTime, String
from sqlalchemy.ext.declarative import declarative_base

from app.database.base import Base

class BinanceRate(Base):
    __tablename__ = "binance_rates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fiat = Column(String(10), nullable=False)       # Ej: "VES"
    asset = Column(String(10), nullable=False)      # Ej: "USDT"
    trade_type = Column(String(10), nullable=False) # "BUY" o "SELL"
    average_price = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
