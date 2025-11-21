"""
Database initialization module
"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import BCVRate, BinanceRate
from app.database.base import Base
from app.config import Config

engine = create_engine(Config.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db(instance_dir: Path):
    """
    Initialize the database and creates the database directory
    """
    Path(instance_dir).mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)