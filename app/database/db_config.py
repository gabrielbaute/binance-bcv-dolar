"""
Database initialization module
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import BCVRate, BinanceRate
from app.database.base import Base
from app.config import Config

engine = create_engine(Config.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Initialize the database
    """
    Base.metadata.create_all(bind=engine)