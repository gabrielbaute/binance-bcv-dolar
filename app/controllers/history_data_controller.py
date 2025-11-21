"""
Controller for persisting historical exchange rate data.
"""
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from app.database.db_config import SessionLocal
from app.database.models.bcv_sql_model import BCVRate
from app.database.models.binance_sql_model import BinanceRate
from app.schemas.bcv_response_schemas import BCVCurrencyResponse
from app.schemas.binance_response_schemas import BinanceResponse

class HistoryDataController:
    """
    Controller for persisting historical exchange rate data.
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _commit_or_rollback(self, session: Session, record) -> None:
        """
        Internal helper to commit a record or rollback on error.

        Args:
            session (Session): The database session.
            record: The record to be saved.
        """
        try:
            session.add(record)
            session.commit()
            self.logger.info(f"Saved record: {record}")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error saving record: {e}")
        finally:
            session.close()

    def save_bcv_rate(self, response: BCVCurrencyResponse) -> None:
        """
        Save a BCV currency rate (USD or EUR).

        Args:
            response (BCVCurrencyResponse): The response object containing the currency rate.
        """
        if not response or not response.rate:
            self.logger.warning("BCV response is empty or invalid, skipping save.")
            return

        session: Session = SessionLocal()
        record = BCVRate(
            currency=response.currency.name,
            rate=response.rate,
            date=response.date or datetime.now()
        )
        self._commit_or_rollback(session, record)

    def save_binance_rate(self, response: BinanceResponse) -> None:
        """
        Save a Binance USDT/Fiat pair average price.

        Args:
            response (BinanceResponse): The response object containing the average price.
        """
        if not response or not response.average_price:
            self.logger.warning("Binance response is empty or invalid, skipping save.")
            return

        session: Session = SessionLocal()
        record = BinanceRate(
            fiat=response.fiat,
            asset=response.asset,
            trade_type=response.trade_type,
            average_price=response.average_price,
            date=datetime.now()
        )
        self._commit_or_rollback(session, record)

    def get_bcv_history(self):
        """
        Get all BCV rates history.
        """
        session: Session = SessionLocal()
        try:
            return session.query(BCVRate).all()
        finally:
            session.close()

    def get_binance_history(self):
        """
        Get all Binance rates history.
        """
        session: Session = SessionLocal()
        try:
            return session.query(BinanceRate).all()
        finally:
            session.close()