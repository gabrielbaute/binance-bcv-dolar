import logging
from pytz import timezone
from apscheduler.schedulers.background import BackgroundScheduler

from app.controllers.history_data_controller import HistoryDataController
from app.services.bcv_scrapper import BCVScraper
from app.services.binance_p2p import BinanceP2P
from app.services.webhook_service import NtfyWebhookService
from app.schemas.webhook_payload_schemas import WebhookPayload
from app.enums import WebhookPriority, Currency


class DolarScheduler():
    def __init__(self):
        self.controller = HistoryDataController()
        self.bcv = BCVScraper()
        self.binance = BinanceP2P()
        self.notifier = NtfyWebhookService()
        self.scheduler = BackgroundScheduler(timezone=timezone("America/Caracas"))
        self.logger = logging.getLogger(self.__class__.__name__)

    def _send_alert(self, title: str, event: str, priority: WebhookPriority, msg: str, tags: str = None):
        """
        Helper method to send notifications.
        Since we are in a Thread (BackgroundScheduler), blocking calls are fine.
        """
        payload = WebhookPayload(
            title=title,
            event=event,
            priority=priority,
            description=msg,
            tags=tags
        )
        self.notifier.emit(payload)

    def save_bcv_rates(self):
        """
        Save BCV rates.
        """
        self.logger.info("Saving BCV rates...")
        try:
            dolar = self.bcv.get_exchange_rate(Currency.DOLAR)
            euro = self.bcv.get_exchange_rate(Currency.EURO)
            
            self.controller.save_bcv_rate(dolar)
            self.controller.save_bcv_rate(euro)

            msg = f"BCV Rates Updated: USD **{dolar.rate} | EUR {euro.rate}**"
            self.logger.info(msg)
            self._send_alert(
                title="BCV Rates Updated",
                event="bcv_update", 
                priority=WebhookPriority.default, 
                msg=msg, 
                tags="bank,venezuela"
            )

        except Exception as e:
            err_msg = f"Error saving BCV rates: {e}"
            self.logger.error(err_msg)
            self._send_alert(
                title="BCV Request Error",
                event="bcv_error", 
                priority=WebhookPriority.high, 
                msg=err_msg, 
                tags="warning,skull"
            )

    def save_binance_rate(self):
        """
        Save Binance rates.
        """
        self.logger.info("Saving Binance rates...")
        try:
            usdt_ves = self.binance.get_usdt_ves_pair()
            self.controller.save_binance_rate(usdt_ves)
            
            # Ajusta según tu objeto real
            price = getattr(usdt_ves, 'average_price', 'N/A') 

            msg = f"Binance USDT/VES Updated: **{price} Bs/USDT**"
            self.logger.info(msg)
            self._send_alert(
                title="Binance USDT/VES Updated",
                event="binance_update",
                priority=WebhookPriority.low,
                msg=msg,
                tags="rocket,chart_with_upwards_trend"
            )
        except Exception as e:
            err_msg = f"Error saving Binance rates: {e}"
            self.logger.error(err_msg)
            self._send_alert(
                title="Binance Rquests Error",
                event="binance_error",
                priority=WebhookPriority.high,
                msg=err_msg,
                tags="warning"
            )


    def scheduler_jobs(self):
        """
        Scheduler jobs.
        """
        self.scheduler.add_job(self.save_bcv_rates, "cron", hour=0, minute=0)
        self.scheduler.add_job(self.save_binance_rate, "cron", hour=6)
        self.scheduler.add_job(self.save_binance_rate, "cron", hour=13)
        self.scheduler.add_job(self.save_binance_rate, "cron", hour=18)

    def start(self):
        """
        Start scheduler.
        """
        self.logger.info("Starting scheduler...")
        self.scheduler_jobs()
        self.scheduler.start()