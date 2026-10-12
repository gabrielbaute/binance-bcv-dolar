import logging
from pytz import timezone
from pydantic import HttpUrl
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import Config
from app.errors import DatabaseOperationError
from app.services import BCVService, BinanceService
from app.services.webhook_service import NtfysService
from app.schemas.webhook_payload_schemas import NTFYPayload
from app.enums import NTFYPriority, Currency, TradeType, FiatCurrency, BinanceAsset

class DolarScheduler:
    def __init__(self, session_maker: async_sessionmaker[AsyncSession], config: Config):
        """
        Initialize the DolarScheduler. This scheduler is responsible for periodically fetching
        exchange rates from BCV and Binance, saving them to the database, and sending notifications
        about updates or errors.
        """
        self.config = config
        self.session_maker = session_maker
        self.notifier = NtfysService(config=self.config)
        self.scheduler = AsyncIOScheduler(timezone=timezone("America/Caracas"))
        self.logger = logging.getLogger(self.__class__.__name__)

    async def _send_alert(
        self,
        topic: str,
        event: str,
        description: str,
        title: Optional[str] = None,
        priority: NTFYPriority = NTFYPriority.DEFAULT,
        tags: Optional[str] = None,
        click: Optional[str] = None,
        icon: Optional[HttpUrl] = None,
        url: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Método para enviar notificaciones al canal NTFY.

        Args:
            event (str): Nombre del evento.
            description (str): Descripción o cuerpo del mensaje.
            title (Optional[str]): Título opcional de la notificación.
            priority (NTFYPriority): Prioridad de la notificación.
            tags (Optional[str]): Etiquetas separadas por comas o emojis.
            click (Optional[str]): Enlace al hacer clic.
            icon (Optional[HttpUrl]): URL del icono/logo de la aplicación.
            url (Optional[str]): URL opcional adjunta.
            data (Optional[Dict[str, Any]]): Metadatos adicionales.

        Returns:
            bool: Código de estado HTTP si se envía, None en caso contrario.
        """
        notification_payload = NTFYPayload(
            event=event,
            description=description,
            title=title,
            priority=priority,
            tags=tags,
            click=click,
            icon=icon,
            url=url,
            data=data,
        )

        code_status = await self.notifier.emit(
            payload=notification_payload,
            topic=topic
        )
        if code_status:
            self.logger.debug(f"Alert send with status {code_status}")
            return True
        else:
            return False

    async def save_bcv_rates(self) -> None:
        async with self.session_maker() as session:
            service = BCVService(config=self.config, database_session=session)
            await self._save_bcv_rates(service)

    async def _save_bcv_rates(self, bcv_service: BCVService) -> None:
        """
        Fetch and persist all officially supported exchange rates from Banco Central de Venezuela.

        Iterates dynamically through the configured currency matrix, handling potential
        individual scraping or persistence anomalies defensively without interrupting the
        overall execution loop. Emits a consolidated notification metrics payload.

        Returns:
            None
        """
        self.logger.info("Starting batch synchronization for all active BCV currency assets...")

        for cur in Currency.to_list():
            try:
                cur_save = await bcv_service.save_rate_to_db(cur)
                if not cur_save:
                    self.logger.error(f"Execution skipped for asset {cur.value}: Persistence routine returned invalid state.")
                    continue

                # Report construction
                msg = f"• {cur.value.upper()}: **{cur_save.rate:.3f} Bs/{cur.value}**"
                self.logger.info(f"Database sync successful for asset metric: {msg}")

            except DatabaseOperationError as e:
                err_msg = f"Database tracking constraint violation saving BCV token {cur.value}: {e}"
                self.logger.error(err_msg)
                await self._send_alert(
                    topic=self.config.NTFY_TOPIC,
                    event="server_error",
                    title="Database Integrity Error",
                    description=err_msg,
                    priority=NTFYPriority.HIGH,
                    tags="rotating_light,skull",
                )
            except Exception as e:
                err_msg = f"Unhandled pipeline disruption isolating BCV token {cur.value}: {e}"
                self.logger.exception(err_msg)
                await self._send_alert(
                    topic=self.config.NTFY_TOPIC,
                    event="bcv_error",
                    title="BCV Request Exception",
                    description=err_msg,
                    priority=NTFYPriority.HIGH,
                    tags="rotating_light,skull",
                )

    async def save_currency_binance_rate(self, currency: FiatCurrency, asset: BinanceAsset) -> bool:
        async with self.session_maker() as session:
            service = BinanceService(database_session=session)
            try:
                return await self._save_currency_binance_rate(currency, asset, service)
            finally:
                await service.close()

    async def _save_currency_binance_rate(
        self,
        currency: FiatCurrency,
        asset: BinanceAsset,
        binance_service: BinanceService
    ) -> bool:
        self.logger.info("Saving Binance rates...")
        try:
            asset_fiat_buy = await binance_service.save_binance_currency(
                currency=currency,
                asset=asset,
                trade_type=TradeType.BUY
            )
            asset_fiat_sell = await binance_service.save_binance_currency(
                currency=currency,
                asset=asset,
                trade_type=TradeType.SELL
            )

            if not asset_fiat_buy or not asset_fiat_sell:
                self.logger.error("Some pairs can't be saved.")
                return False

            msg = f"Binance USDT/VES Updated: **{asset_fiat_buy.average_price:.3f} {currency.value}/{asset.value}** at Buy, **{asset_fiat_sell.average_price:.3f} {currency.value}/{asset.value}** at Sell"
            self.logger.info(msg)
            return True

        except DatabaseOperationError as e:
            err_msg = f"Dabasa operation error error saving Binance rates: {e}"
            self.logger.error(err_msg)
            await self._send_alert(
                topic=self.config.NTFY_TOPIC,
                title="Server Error",
                event="server_error",
                description=err_msg,
                priority=NTFYPriority.HIGH,
                tags="rotating_light,skull",
            )
            raise
        except Exception as e:
            err_msg = f"Error saving Binance rates: {e}"
            self.logger.error(err_msg)
            await self._send_alert(
                topic=self.config.NTFY_TOPIC,
                title="Binance Rquests Error",
                event="binance_error",
                description=err_msg,
                priority=NTFYPriority.HIGH,
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

    async def send_binance_android_notification(self) -> None:
        """
        Sends a push notification to android topic
        """
        async with self.session_maker() as session:
            service = BinanceService(database_session=session)
            pairs_buy = await service.get_last_saved_binance_fiat(
                fiat=FiatCurrency.VES,
                asset=BinanceAsset.USDT,
                trade_type=TradeType.BUY
            )
            pairs_sell = await service.get_last_saved_binance_fiat(
                fiat=FiatCurrency.VES,
                asset=BinanceAsset.USDT,
                trade_type=TradeType.SELL
            )
            msg = f"{pairs_buy.average_price:.3f} VES/USDT (Compra) • {pairs_sell.average_price:.3f} VES/USDT (Venta)"
            await self._send_alert(
                topic=self.config.NTFY_MOBILE_PUSH_TOPIC,
                title="Binance USDT/VES AHORA",
                event="binance_update",
                description=msg,
                priority=NTFYPriority.DEFAULT,
                tags="binance_update"
            )


    async def send_bcv_android_notification(self) -> None:
        """
        Sends a push notification to android topic
        """
        async with self.session_maker() as session:
            service = BCVService(config=self.config, database_session=session)
            pairs = await service.get_all_exchange_rates()
            msg = f"{pairs.dolar.rate:.3f} VES/USD • {pairs.euro.rate:3f} VES/EUR"
            await self._send_alert(
                topic=self.config.NTFY_MOBILE_PUSH_TOPIC,
                title="BCV HOY",
                event="bcv_update",
                description=msg,
                priority=NTFYPriority.DEFAULT,
                tags="bcv_update"
            )

    def scheduler_jobs(self) -> None:
        """
        Dynamically registers execution rules driven by environmental variables parsed by Pydantic.
        """
        self.scheduler.add_job(
            self.save_bcv_rates,
            CronTrigger.from_crontab(self.config.BCV_CRON),
            id="bcv_rates_job",
            max_instances=1,
            coalesce=True,
        )
        self.logger.info(f"BCV successfully scheduled with cron {self.config.BCV_CRON}")

        self.scheduler.add_job(
            self.save_binance_ves_usdt_rate,
            CronTrigger.from_crontab(self.config.BINANCE_VES_CRON),
            id="binance_ves_job",
            max_instances=1,
            coalesce=True,
        )
        self.logger.info(f"VES/USDT pair successfully scheduled with cron {self.config.BINANCE_VES_CRON}")

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
                        id=f"binance_extra_{fiat_str.lower()}_job",
                        max_instances=1,
                        coalesce=True,
                    )
                    self.logger.info(f"Successfully scheduled dynamic tracking for {fiat_str} with cron '{self.config.BINANCE_EXTRA_CRON}'")
                except ValueError:
                    self.logger.error(f"Currency '{fiat_str}' from config is not a supported FiatCurrency Enum value. Skipping.")

        binance_android_cron = self.config.BINANCE_NOTIFICATIONS_CRON_JOB
        if binance_android_cron:
            self.scheduler.add_job(
                self.send_binance_android_notification,
                CronTrigger.from_crontab(self.config.BINANCE_NOTIFICATIONS_CRON_JOB),
                id="binance_android_job",
                max_instances=1,
                coalesce=True,
            )
            self.logger.info("Cronjob de notificacion Push Establecido para Binance.")

        bcv_android_cron = self.config.BCV_NOTIFICATIONS_CRON_JOB
        if bcv_android_cron:
            self.scheduler.add_job(
                self.send_bcv_android_notification,
                CronTrigger.from_crontab(self.config.BCV_NOTIFICATIONS_CRON_JOB),
                id="bvc_android_job",
                max_instances=1,
                coalesce=True,
            )
            self.logger.info("Cronjob de notificacion Push Establecido para BCV.")
    def start(self) -> None:
        """
        Start the asynchronous scheduler loops.
        """
        self.logger.info("Starting automated asynchronous scheduler engine...")
        self.scheduler_jobs()
        self.scheduler.start()

    async def shutdown(self) -> None:
        """Stop scheduler jobs and release owned resources."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
        await self.notifier.close()
