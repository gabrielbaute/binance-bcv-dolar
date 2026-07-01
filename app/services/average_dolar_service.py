"""Average dolar exchange rate module."""
import logging
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.bcv_service import BCVService
from app.services.binance_service import BinanceService
from app.schemas import DolarResponse, RealTimeDolarResponse
from app.enums import Currency, FiatCurrency, BinanceAsset, TradeType

class DolarVenezuelaService:
    """
    Service for getting the average dolar exchange rate.
    """
    def __init__(self, databasesession: AsyncSession):
        """
        Initialize the DolarVenezuelaService.

        Args:
            databasesession (AsyncSession): The database session.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.binance = BinanceService(database_session=databasesession)
        self.bcv = BCVService(database_session=databasesession)

    def get_real_time_average_dolar(self) -> Optional[RealTimeDolarResponse]:
        """
        Get the average dolar exchange rate.

        Returns:
            Optional[RealTimeDolarResponse]: Real-time average dolar exchange rate data.
        """
        self.logger.info("Getting average dolar exchange rate")
        binance_usdt_ves = self.binance.get_real_time_usdt_ves_pair()
        bcv_dolar = self.bcv.get_real_time_exchange_rate(Currency.DOLAR)
        bcv_euro = self.bcv.get_real_time_exchange_rate(Currency.EURO)

        if not binance_usdt_ves or not bcv_dolar:
            self.logger.error("Error getting data for average dolar exchange rate")
            return None

        average_price = (binance_usdt_ves.average_price + bcv_dolar.rate) / 2

        return RealTimeDolarResponse(
            bcv_dolar=bcv_dolar,
            bcv_euro=bcv_euro,
            binance_usdt_ves_buy=binance_usdt_ves,
            average_usdt_ves=average_price,
            date=datetime.now()
        )

    async def get_average_dolar_last_register(self) -> Optional[DolarResponse]:
        """
        Get the last registered average dolar exchange rate.

        Returns:
            Optional[DolarResponse]: Last registered average dolar exchange rate data.
        """
        self.logger.info("Getting last registered average dolar exchange rate")
        binance_usdt_ves = await self.binance.get_last_saved_binance_fiat(
            fiat=FiatCurrency.VES, asset=BinanceAsset.USDT, trade_type=TradeType.BUY
        )
        bcv_dolar = await self.bcv.get_exchange_rate(Currency.DOLAR)
        bcv_euro = await self.bcv.get_exchange_rate(Currency.EURO)

        if not binance_usdt_ves or not bcv_dolar:
            self.logger.error("Error getting data for last registered average dolar exchange rate")
            return None

        average_price = (binance_usdt_ves.average_price + bcv_dolar.rate) / 2

        return DolarResponse(
            bcv_dolar=bcv_dolar,
            bcv_euro=bcv_euro,
            binance_usdt_ves_buy=binance_usdt_ves,
            average_usdt_ves=average_price,
            date=datetime.now()
        )