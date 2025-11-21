from sqlalchemy import Column, Integer, Float, DateTime, String
from sqlalchemy.ext.declarative import declarative_base

from app.database.base import Base

class BCVRate(Base):
    __tablename__ = "bcv_rates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency = Column(String(10), nullable=False)  # "USD" o "EUR"
    rate = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
