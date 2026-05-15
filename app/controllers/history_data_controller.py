"""
Controller for persisting historical exchange rate data.
"""
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from app.enums.currecies_enum import Currency
from app.database.db_config import SessionLocal
from app.database.models.bcv_sql_model import BCVRate
from app.database.models.binance_sql_model import BinanceRate
from app.schemas.bcv_response_schemas import BCVCurrencyResponse
from app.schemas.binance_response_schemas import BinanceResponse
from app.schemas.history_response_schemas import BinanceHistoryItem, BinanceHistoryResponse, BCVHistoryItem, BCVHistoryResponse

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

    def get_bcv_history(
            self, 
            start_date: datetime = None, 
            end_date: datetime =None, 
            currency: str = None
        ) -> BCVHistoryResponse:
        """
        Get all BCV rates history.

        Args:
            start_date (datetime, optional): Start date for the query.
            end_date (datetime, optional): End date for the query.
            currency (str, optional): Currency to filter the query (DOLAR or EURO).
        """
        session = SessionLocal()
        query = session.query(BCVRate)
        if currency:
            query = query.filter(BCVRate.currency == currency)
        if start_date:
            query = query.filter(BCVRate.date >= start_date)
        if end_date:
            query = query.filter(BCVRate.date < end_date)
        results = query.all()
        session.close()
        
        results = [
            BCVHistoryItem(
                id=result.id,
                currency=result.currency,
                rate=result.rate,
                date=result.date
            )
            for result in results
        ]

        return BCVHistoryResponse(count=len(results), history=results)

    def get_binance_history(
            self, 
            start_date: datetime = None, 
            end_date: datetime = None, 
            fiat: str = None, 
            asset: str = None, 
            trade_type: str = None
        ) -> BinanceHistoryResponse:
        """
        Get all Binance rates history.

        Args:
            start_date (datetime, optional): Start date for the query.
            end_date (datetime, optional): End date for the query.
            fiat (str, optional): Fiat currency to filter the query.
            asset (str, optional): Asset to filter the query (USDT by default).
            trade_type (str, optional): Trade type to filter the query (actually only BUY works for now).
        """
        session = SessionLocal()
        query = session.query(BinanceRate)
        if fiat:
            query = query.filter(BinanceRate.fiat == fiat)
        if asset:
            query = query.filter(BinanceRate.asset == asset)
        if trade_type:
            query = query.filter(BinanceRate.trade_type == trade_type)
        if start_date:
            query = query.filter(BinanceRate.date >= start_date)
        if end_date:
            query = query.filter(BinanceRate.date < end_date)
        results = query.all()
        session.close()

        results = [
            BinanceHistoryItem(
                id=result.id,
                fiat=result.fiat,
                asset=result.asset,
                trade_type=result.trade_type,
                average_price=result.average_price,
                date=result.date
            )
            for result in results
        ]

        return BinanceHistoryResponse(count=len(results), history=results)