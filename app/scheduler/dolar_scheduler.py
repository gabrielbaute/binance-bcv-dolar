import logging
from pytz import timezone

from apscheduler.schedulers.background import BackgroundScheduler
from app.controllers.history_data_controller import HistoryDataController
from app.services.bcv_scrapper import BCVScraper
from app.services.binance_p2p import BinanceP2P

class DolarScheduler():
    def __init__(self):
        self.controller = HistoryDataController()
        self.bcv = BCVScraper()
        self.binance = BinanceP2P()
        self.scheduler = BackgroundScheduler(timezone=timezone("America/Caracas"))
        self.logger = logging.getLogger(self.__class__.__name__)

    def save_bcv_rates(self):
        """
        Save BCV rates.
        """
        self.logger.info("Saving BCV rates...")
        try:
            dolar = self.bcv.get_exchange_rate("USD")
            euro = self.bcv.get_exchange_rate("EUR")
            self.controller.save_bcv_rate(dolar)
            self.controller.save_bcv_rate(euro)
        except Exception as e:
            self.logger.error(f"Error saving BCV rates: {e}")

    def save_binance_rate(self):
        """
        Save Binance rates.
        """
        self.logger.info("Saving Binance rates...")
        try:
            usdt_ves = self.binance.get_usdt_ves_pair()
            self.controller.save_binance_rate(usdt_ves)
        except Exception as e:
            self.logger.error(f"Error saving Binance rates: {e}")


    def scheduler_jobs(self):
        """
        Scheduler jobs.
        """
        self.scheduler.add_job(self.save_bcv_rates, "cron", hour=0, minute=0)
        self.scheduler.add_job(self.save_binance_rate, "cron", hour=9)
        self.scheduler.add_job(self.save_binance_rate, "cron", hour=15)
        self.scheduler.add_job(self.save_binance_rate, "cron", hour=21)

    def start(self):
        """
        Start scheduler.
        """
        self.logger.info("Starting scheduler...")
        self.scheduler_jobs()
        self.scheduler.start()