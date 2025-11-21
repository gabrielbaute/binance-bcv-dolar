"""Fiat Pair Service module."""
import logging
from datetime import datetime
from typing import Optional

from app.schemas import BinanceResponse, FiatPairResponse
from app.services.binance_p2p import BinanceP2P


class FiatExchengeService():
    """
    Service for getting fiat exchange rates.
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.binance = BinanceP2P()

    def get_usdt_pair(self, fiat: str = "VES", trade_type: str = "BUY") -> BinanceResponse:
        """
        Get the USDT/FIAT pair.

        Args:
            fiat (str, optional): Fiat currency. Defaults to "VES".

        Returns:
            BinanceResponse: USDT/VES pair data.
        """
        return self.binance.get_pair(fiat=fiat, asset="USDT", trade_type=trade_type, rows=20)
    
    def calculate_exchange_rate(self, fiat_1: BinanceResponse, fiat_2: BinanceResponse) -> Optional[float]:
        """
        Calculate the exchange rate from Fiat 1 to Fiat 2.
        
        Args:
            fiat_1 (BinanceResponse): Fiat 1 response.
            fiat_2 (BinanceResponse): Fiat 2 response.

        Returns:
            float: Exchange rate.
        """
        if not fiat_1 or not fiat_2:
            self.logger.error("Error calculating exchange rate")
            return None
        return fiat_2.average_price / fiat_1.average_price

    def get_pair(self, fiat_1: str = "VES", fiat_2: str = "PEN") -> FiatPairResponse:
        """
        Get the pair.

        Args:
            fiat_1 (str, optional): Fiat 1 currency. Defaults to "VES".
            fiat_2 (str, optional): Fiat 2 currency. Defaults to "PEN".

        Returns:
            FiatPairResponse: Fiat pair data.
        """
        self.logger.info(f"Getting all data for pair: {fiat_1} - {fiat_2}")

        fiat_1_p2p_buy = self.get_usdt_pair(fiat=fiat_1, trade_type="BUY")
        fiat_1_p2p_sell = self.get_usdt_pair(fiat=fiat_1, trade_type="SELL")
        fiat_2_p2p_buy = self.get_usdt_pair(fiat=fiat_2, trade_type="BUY")
        fiat_2_p2p_sell = self.get_usdt_pair(fiat=fiat_2, trade_type="SELL")
        exchange_rate_f1_f2 = self.calculate_exchange_rate(fiat_1_p2p_buy, fiat_2_p2p_sell)
        exchange_rate_f2_f1 = self.calculate_exchange_rate(fiat_2_p2p_buy, fiat_1_p2p_sell)

        return FiatPairResponse(
            fiat_1_p2p_buy=fiat_1_p2p_buy,
            fiat_1_p2p_sell=fiat_1_p2p_sell,
            fiat_2_p2p_buy=fiat_2_p2p_buy,
            fiat_2_p2p_sell=fiat_2_p2p_buy,
            exchange_rate_f1_f2=exchange_rate_f1_f2,
            exchange_rate_f2_f1=exchange_rate_f2_f1,
            date=datetime.now()
        ) 