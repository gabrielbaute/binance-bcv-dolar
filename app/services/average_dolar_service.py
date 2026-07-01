"""Average dolar exchange rate module."""
import logging
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors import RegisterNotFoundError
from app.services.bcv_service import BCVService
from app.services.binance_service import BinanceService
from app.schemas import DolarResponse, RealTimeDolarResponse
from app.enums import Currency, FiatCurrency, BinanceAsset, TradeType

class DolarVenezuelaService:
    """
    Service for calculating unified composite exchange rate matrices inside the Venezuelan market.
    """
    def __init__(self, database_session: AsyncSession):
        """
        Initialize the DolarVenezuelaService with appropriate operational tracking contexts.

        Args:
            database_session (AsyncSession): Active transactional instance mapping to persistent storage layers.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.bcv = BCVService(databasesession=database_session)
        self.binance = BinanceService(databasesession=database_session)

    def get_real_time_average_dolar(self) -> Optional[RealTimeDolarResponse]:
        """
        Synthesize immediate real-time average metrics bridging central bank rates and P2P order books.

        Returns:
            Optional[RealTimeDolarResponse]: Composite summary enclosing validated realtime data matrices, or None if upstream provider blocks fail to resolve pricing.
        """
        self.logger.info("Getting average dolar exchange rate")
        
        binance_usdt_ves = self.binance.get_real_time_pair(
            fiat=FiatCurrency.VES, asset=BinanceAsset.USDT, trade_type=TradeType.BUY
        )
        bcv_dolar = self.bcv.get_real_time_exchange_rate(Currency.DOLAR)
        bcv_euro = self.bcv.get_real_time_exchange_rate(Currency.EURO)

        if not binance_usdt_ves or not bcv_dolar:
            self.logger.error("Error getting data for average dolar exchange rate: Missing provider baseline data.")
            return None

        if binance_usdt_ves.average_price is None or bcv_dolar.rate is None:
            self.logger.warning("Upstream payload evaluated contains null pricing metrics. Cannot compute average.")
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
        Retrieve and compute the mean exchange values based on the last locally synchronized tracking benchmarks.

        Returns:
            Optional[DolarResponse]: Consolidated aggregate of historical baseline indices, or None if any source track resolves to an unrecoverable exception.
        """
        self.logger.info("Getting last registered average dolar exchange rate")
        
        try:
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
            
        except RegisterNotFoundError as e:
            self.logger.warning(f"Aborting average aggregation. A baseline ledger track was missing: {e.message}")
            return None