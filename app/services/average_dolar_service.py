"""Average dolar exchange rate module."""
import logging
from datetime import datetime

from app.enums import Currency
from app.schemas import DolarResponse, BCVCurrencyResponse, BinanceResponse
from app.services.binance_p2p import BinanceP2P
from app.services.bcv_scrapper import BCVScraper

class DolarService:
    """
    Service for getting the average dolar exchange rate.
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.binance = BinanceP2P()
        self.bcv = BCVScraper()

    def get_average_dolar(self) -> DolarResponse:
        """
        Get the average dolar exchange rate.

        Returns:
            DolarResponse: Average dolar exchange rate data.
        """
        self.logger.info("Getting average dolar exchange rate")
        binance_usdt_ves = self.binance.get_usdt_ves_pair()
        bcv_dolar = self.bcv.get_exchange_rate(Currency.DOLAR)
        bcv_euro = self.bcv.get_exchange_rate(Currency.EURO)

        if not binance_usdt_ves or not bcv_dolar:
            self.logger.error("Error getting data for average dolar exchange rate")
            return None

        average_price = (binance_usdt_ves.average_price + bcv_dolar.rate) / 2

        return DolarResponse(
            bcv_dolar=bcv_dolar,
            bcv_euro=bcv_euro,
            binance_usdt_ves_buy=binance_usdt_ves,
            average_usdt_ves=average_price,
            date=datetime.now()
        )
