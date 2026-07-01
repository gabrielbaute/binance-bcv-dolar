import logging
from pytz import timezone
from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import Config
from app.errors import DatabaseOperationError
from app.services import BCVService, BinanceService
from app.services.webhook_service import NtfyWebhookService
from app.schemas.webhook_payload_schemas import WebhookPayload
from app.enums import WebhookPriority, Currency, TradeType, FiatCurrency, BinanceAsset


class DolarScheduler():
    def __init__(self, databasesession: AsyncSession, config: Config):
        """
        Initialize the DolarScheduler. This scheduler is responsible for periodically fetching exchange rates from BCV and Binance, saving them to the database, and sending notifications about updates or errors.
        """
        self.config = config
        self.notifier = NtfyWebhookService()
        self.binance_service = BinanceService(databasesession=databasesession)
        self.bcv_service = BCVService(databasesession=databasesession)
        self.scheduler = AsyncIOScheduler(timezone=timezone("America/Caracas"))
        self.logger = logging.getLogger(self.__class__.__name__)

    def _send_alert(self, title: str, event: str, priority: WebhookPriority, msg: str, tags: str = None):
        """
        Helper method to send notifications.

        Args:
            title (str): Title of notification
            event (str): Event of notification
            priority (WebhookPriority): Priority of notification
            msg (str): Message of notification
            tags (str, optional): Tags of notification. Defaults to None.
        """
        payload = WebhookPayload(
            title=title,
            event=event,
            priority=priority,
            description=msg,
            tags=tags
        )
        self.notifier.emit(payload)

    async def save_bcv_rates(self) -> None:
        """
        Save BCV rates.

        Returns:
            None

        Exception:
            Logs error and sends alert if there is an issue fetching or saving BCV rates.
        """
        self.logger.info("Saving BCV rates...")
        try:
            dolar = await self.bcv_service.save_rate_to_db(Currency.DOLAR)
            if not dolar:
                self.logger.error(f"Error saving {Currency.DOLAR.value} on database.")

            euro = await self.bcv_service.save_rate_to_db(Currency.EURO)
            if not euro:
                self.logger.error(f"Error saving {Currency.EURO.value} on database.")

            msg = f"BCV Rates Updated: USD **{dolar.rate} | EUR {euro.rate}**"
            self.logger.info(msg)
            self._send_alert(
                title="BCV Rates Updated",
                event="bcv_update", 
                priority=WebhookPriority.default, 
                msg=msg, 
                tags="bank,venezuela"
            )

        except DatabaseOperationError as e:
            err_msg = f"Dabasa operation error error saving BCV rates: {e}"
            self.logger.error(err_msg)
            self._send_alert(
                title="Server Error",
                event="server_error", 
                priority=WebhookPriority.high, 
                msg=err_msg, 
                tags="warning,skull"
            )
        except Exception as e:
            err_msg = f"Unknown error saving BCV rates: {e}"
            self.logger.error(err_msg)
            self._send_alert(
                title="BCV Request Error",
                event="bcv_error", 
                priority=WebhookPriority.high, 
                msg=err_msg, 
                tags="warning,skull"
            )

    async def save_currency_binance_rate(self, currency: FiatCurrency, asset: BinanceAsset) -> bool:
        self.logger.info("Saving Binance rates...")
        try:
            asset_fiat_buy = await self.binance_service.save_binance_currency(
                currency=currency,
                asset=asset,
                trade_type=TradeType.BUY
            )
            if not asset_fiat_buy:
                self.logger.error(f"Error saving {currency.value} at {TradeType.BUY.value} type operation on Database.")
            asset_fiat_sell = await self.binance_service.save_binance_currency(
                currency=currency,
                asset=asset,
                trade_type=TradeType.SELL
            )
            if not asset_fiat_sell:
                self.logger.error(f"Error saving {currency.value} at {TradeType.SELL.value} type operation on Database.")

            msg = f"Binance USDT/VES Updated: **{asset_fiat_buy.average_price} {currency.value}/{asset.value}** at Buy, **{asset_fiat_sell.average_price} {currency.value}/{asset.value}** at Sell"
            self.logger.info(msg)
            self._send_alert(
                title="Binance USDT/VES Updated",
                event="binance_update",
                priority=WebhookPriority.low,
                msg=msg,
                tags="rocket,chart_with_upwards_trend"
            )
            if not asset_fiat_buy or not asset_fiat_sell:
                self.logger.error(f"Some pairs can't be saved.")
                return False
            return True
        
        except DatabaseOperationError as e:
            err_msg = f"Dabasa operation error error saving Binance rates: {e}"
            self.logger.error(err_msg)
            self._send_alert(
                title="Server Error",
                event="server_error", 
                priority=WebhookPriority.high, 
                msg=err_msg, 
                tags="warning,skull"
            )
            raise
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
            raise

    async def save_binance_ves_usdt_rate(self) -> None:
        """
        Save Binance rates for VES/USDT pair.
        """
        await self.save_currency_binance_rate(
            currency=FiatCurrency.VES,
            asset=BinanceAsset.USDT
        )

    def scheduler_jobs(self) -> None:
        """
        Dynamically registers execution rules driven by environmental variables parsed by Pydantic.
        """
        self.scheduler.add_job(
            self.save_bcv_rates, 
            CronTrigger.from_crontab(self.config.BCV_CRON),
            id="bcv_rates_job"
        )
        
        self.scheduler.add_job(
            self.save_binance_ves_usdt_rate, 
            CronTrigger.from_crontab(self.config.BINANCE_VES_CRON),
            id="binance_ves_job"
        )

        extra_fiats_raw = self.config.BINANCE_EXTRA_FIATS
        if extra_fiats_raw:
            fiats_to_track = [f.strip().upper() for f in extra_fiats_raw.split(",") if f.strip()]
            
            for fiat_str in fiats_to_track:
                try:
                    fiat_enum = FiatCurrency(fiat_str)
                    
                    self.scheduler.add_job(
                        self.save_currency_binance_rate,
                        CronTrigger.from_crontab(self.config.BINANCE_EXTRA_CRON),
                        args=[fiat_enum, BinanceAsset.USDT],
                        id=f"binance_extra_{fiat_str.lower()}_job"
                    )
                    self.logger.info(f"Successfully scheduled dynamic tracking for {fiat_str} with cron '{self.config.BINANCE_EXTRA_CRON}'")
                except ValueError:
                    self.logger.error(f"Currency '{fiat_str}' from config is not a supported FiatCurrency Enum value. Skipping.")

    def start(self) -> None:
        """
        Start the asynchronous scheduler loops.
        """
        self.logger.info("Starting automated asynchronous scheduler engine...")
        self.scheduler_jobs()
        self.scheduler.start()