"""Fiat Pair Service module."""
import logging
from datetime import datetime
from typing import Optional, Union, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.binance_service import BinanceService
from app.enums import FiatCurrency, BinanceAsset, TradeType
from app.schemas import (
    FiatPairResponse,
    BinanceCurrencyResponse,
    BinanceRealTimeResponse
)

class FiatExchangeService():
    """
    Service for getting fiat exchange rates with USDT.
    """
    def __init__(self, database_session: AsyncSession):
        self.database_session = database_session
        self.logger = logging.getLogger(self.__class__.__name__)
        self.binance = BinanceService(databasesession=database_session)

    def _get_real_time_usdt_pair(self, fiat: FiatCurrency, trade_type: TradeType) -> Optional[BinanceRealTimeResponse]:
        """
        Get the real-time USDT/FIAT pair.

        Args:
            fiat (FiatCurrency): Fiat currency.
            trade_type (TradeType): Trade type (BUY or SELL).

        Returns:
            Optional[BinanceRealTimeResponse]: Real-time USDT/FIAT pair data.
        """
        self.logger.info(f"Getting real-time USDT/{fiat} pair")
        pair = self.binance.get_real_time_pair(fiat=fiat, asset=BinanceAsset.USDT, trade_type=trade_type)
        return pair

    async def _get_usdt_pair_from_database(self, fiat: FiatCurrency, trade_type: TradeType) -> BinanceCurrencyResponse:
        """
        Retrieve the historical benchmark record for a specific fiat/USDT pair from database tracking.

        Args:
            fiat (FiatCurrency): Target fiat currency destination token.
            trade_type (TradeType): Order book context perspective (BUY or SELL).

        Returns:
            BinanceCurrencyResponse: Validated output model database registry matching parameters.
        """
        pair = await self.binance.get_last_saved_binance_fiat(
            fiat=fiat, asset=BinanceAsset.USDT, trade_type=trade_type
        )
        return pair

    def _calculate_exchange_rate(
            self, 
            fiat_1: Union[BinanceCurrencyResponse, BinanceRealTimeResponse], 
            fiat_2: Union[BinanceCurrencyResponse, BinanceRealTimeResponse]
    ) -> Optional[float]:
        """
        Calculate the cross exchange rate from Fiat 1 to Fiat 2 utilizing standard bridge pricing.
        
        Args:
            fiat_1 (Union[BinanceCurrencyResponse, BinanceRealTimeResponse]): Source fiat platform asset payload.
            fiat_2 (Union[BinanceCurrencyResponse, BinanceRealTimeResponse]): Target fiat platform asset payload.

        Returns:
            Optional[float]: Calculated cross rate ratio value, or None if evaluation matrices lack pricing.
        """
        if not fiat_1 or not fiat_2:
            self.logger.error("Error calculating exchange rate: One or both parameters are missing.")
            return None
            
        # Protegemos contra valores nulos o divisiones por cero en operaciones P2P en tiempo real
        if fiat_1.average_price is None or fiat_2.average_price is None or fiat_1.average_price == 0:
            self.logger.warning(f"Incomplete pricing data matrices to process ratio cross between {fiat_1.fiat} and {fiat_2.fiat}")
            return None
            
        return fiat_2.average_price / fiat_1.average_price

    async def get_pair(self, fiat_1: FiatCurrency, fiat_2: FiatCurrency) -> FiatPairResponse:
        """
        Fetch from persistent layer and assemble cross-pricing metrics between two specific fiat currencies.

        Args:
            fiat_1 (FiatCurrency): Source operational currency token context.
            fiat_2 (FiatCurrency): Destination target currency token context.

        Returns:
            FiatPairResponse: Validated structured summary encompassing baseline metrics and cross rates.
        """
        self.logger.info(f"Getting all data for pair: {fiat_1.value} - {fiat_2.value}")

        # Pasamos el trade_type correcto a cada llamada de base de datos
        fiat_1_p2p_buy = await self._get_usdt_pair_from_database(fiat=fiat_1, trade_type=TradeType.BUY)
        fiat_1_p2p_sell = await self._get_usdt_pair_from_database(fiat=fiat_1, trade_type=TradeType.SELL)
        fiat_2_p2p_buy = await self._get_usdt_pair_from_database(fiat=fiat_2, trade_type=TradeType.BUY)
        fiat_2_p2p_sell = await self._get_usdt_pair_from_database(fiat=fiat_2, trade_type=TradeType.SELL)
        
        exchange_rate_f1_f2 = self._calculate_exchange_rate(fiat_1_p2p_buy, fiat_2_p2p_sell)
        exchange_rate_f2_f1 = self._calculate_exchange_rate(fiat_2_p2p_buy, fiat_1_p2p_sell)

        return FiatPairResponse(
            fiat_1_p2p_buy=fiat_1_p2p_buy,
            fiat_1_p2p_sell=fiat_1_p2p_sell,
            fiat_2_p2p_buy=fiat_2_p2p_buy,
            fiat_2_p2p_sell=fiat_2_p2p_sell,
            average_exchange_rate_f1_f2=exchange_rate_f1_f2,
            average_exchange_rate_f2_f1=exchange_rate_f2_f1,
            date=datetime.now()
        )
    
    #TODO: This method requiere a refactor and detailed review, as it is complex and has multiple responsibilities. Consider breaking it down into smaller methods for clarity and maintainability.
    async def get_historical_pair(
            self, 
            fiat_1: FiatCurrency, 
            fiat_2: FiatCurrency,
            start_date: datetime,
            end_date: datetime,
            skip: int = 0,
            limit: int = 100
    ) -> list[FiatPairResponse]:
        """
        Fetch chronologically synchronized cross-pricing metrics between two specific fiat currencies.

        Args:
            fiat_1 (FiatCurrency): Source operational fiat currency.
            fiat_2 (FiatCurrency): Target destination fiat currency.
            start_date (datetime): Lower chronological boundary.
            end_date (datetime): Upper chronological boundary.
            skip (int): Pagination offset window marker. Defaults to 0.
            limit (int): Pagination maximum payload constraints. Defaults to 100.

        Returns:
            list[FiatPairResponse]: Aligned sequence of historical cross rate contexts.
        """
        self.logger.info(f"Getting historical data for pair: {fiat_1.value} - {fiat_2.value} from {start_date} to {end_date}")

        f1_buy_res = await self.binance.get_binance_pair_by_time_range(
            fiat=fiat_1, asset=BinanceAsset.USDT, trade_type=TradeType.BUY, 
            start_time=start_date, end_time=end_date, skip=skip, limit=limit
        )
        f1_sell_res = await self.binance.get_binance_pair_by_time_range(
            fiat=fiat_1, asset=BinanceAsset.USDT, trade_type=TradeType.SELL, 
            start_time=start_date, end_time=end_date, skip=skip, limit=limit
        )
        f2_buy_res = await self.binance.get_binance_pair_by_time_range(
            fiat=fiat_2, asset=BinanceAsset.USDT, trade_type=TradeType.BUY, 
            start_time=start_date, end_time=end_date, skip=skip, limit=limit
        )
        f2_sell_res = await self.binance.get_binance_pair_by_time_range(
            fiat=fiat_2, asset=BinanceAsset.USDT, trade_type=TradeType.SELL, 
            start_time=start_date, end_time=end_date, skip=skip, limit=limit
        )

        def build_timeline_map(currencies):
            return {currency.date.strftime("%Y-%m-%d %H:%M"): currency for currency in currencies}

        map_f1_buy = build_timeline_map(f1_buy_res.currencies)
        map_f1_sell = build_timeline_map(f1_sell_res.currencies)
        map_f2_buy = build_timeline_map(f2_buy_res.currencies)
        map_f2_sell = build_timeline_map(f2_sell_res.currencies)

        historic: list[FiatPairResponse] = []

        for timeline_key, f1_buy_item in map_f1_buy.items():
            f1_buy_item = map_f1_buy.get(timeline_key)
            f1_sell_item = map_f1_sell.get(timeline_key)
            f2_buy_item = map_f2_buy.get(timeline_key)
            f2_sell_item = map_f2_sell.get(timeline_key)

            if not (f1_buy_item and f1_sell_item and f2_buy_item and f2_sell_item):
                self.logger.debug(f"Skipping timeline frame {timeline_key} due to incomplete metrics alignment.")
                continue

            historic.append(
                FiatPairResponse(
                    fiat_1_p2p_buy=f1_buy_item,
                    fiat_1_p2p_sell=f1_sell_item,
                    fiat_2_p2p_buy=f2_buy_item,
                    fiat_2_p2p_sell=f2_sell_item,
                    average_exchange_rate_f1_f2=self._calculate_exchange_rate(f1_buy_item, f2_sell_item),
                    average_exchange_rate_f2_f1=self._calculate_exchange_rate(f2_buy_item, f1_sell_item),
                    date=f1_buy_item.date
                )
            )

        return historic

    def get_real_time_pair(self, fiat_1: FiatCurrency, fiat_2: FiatCurrency) -> FiatPairResponse:
        """
        Fetch real-time cross-pricing metrics between two specific fiat currencies from Binance P2P.

        Args:
            fiat_1 (FiatCurrency): First fiat currency.
            fiat_2 (FiatCurrency): Second fiat currency.

        Returns:
            FiatPairResponse: Real-time USDT/FIAT pair data.
        """
        self.logger.info(f"Getting real-time {fiat_1.value}/{fiat_2.value} pair")

        fiat_1_p2p_buy = self._get_real_time_usdt_pair(fiat=fiat_1, trade_type=TradeType.BUY)
        fiat_1_p2p_sell = self._get_real_time_usdt_pair(fiat=fiat_1, trade_type=TradeType.SELL)
        fiat_2_p2p_buy = self._get_real_time_usdt_pair(fiat=fiat_2, trade_type=TradeType.BUY)
        fiat_2_p2p_sell = self._get_real_time_usdt_pair(fiat=fiat_2, trade_type=TradeType.SELL)
        exchange_rate_f1_f2 = self._calculate_exchange_rate(fiat_1_p2p_buy, fiat_2_p2p_sell)
        exchange_rate_f2_f1 = self._calculate_exchange_rate(fiat_2_p2p_buy, fiat_1_p2p_sell)

        return FiatPairResponse(
            fiat_1_p2p_buy=fiat_1_p2p_buy,
            fiat_1_p2p_sell=fiat_1_p2p_sell,
            fiat_2_p2p_buy=fiat_2_p2p_buy,
            fiat_2_p2p_sell=fiat_2_p2p_sell,
            average_exchange_rate_f1_f2=exchange_rate_f1_f2,
            average_exchange_rate_f2_f1=exchange_rate_f2_f1,
            date=datetime.now()
        )