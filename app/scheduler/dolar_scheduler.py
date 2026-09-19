import logging
from pytz import timezone
from pydantic import HttpUrl
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import Config
from app.errors import DatabaseOperationError
from app.services import BCVService, BinanceService
from app.services.webhook_service import NtfysService
from app.schemas.webhook_payload_schemas import NTFYPayload
from app.enums import NTFYPriority, Currency, TradeType, FiatCurrency, BinanceAsset


class DolarScheduler():
    def __init__(self, databasesession: AsyncSession, config: Config):
        """
        Initialize the DolarScheduler. This scheduler is responsible for periodically fetching exchange rates from BCV and Binance, saving them to the database, and sending notifications about updates or errors.
        """
        self.config = config
        self.notifier = NtfysService(config=self.config)
        self.binance_service = BinanceService(databasesession=databasesession)
        self.bcv_service = BCVService(databasesession=databasesession)
        self.scheduler = AsyncIOScheduler(timezone=timezone("America/Caracas"))
        self.logger = logging.getLogger(self.__class__.__name__)

    async def _send_alert(
        self,
        event: str,
        description: str,
        title: Optional[str] = None,
        priority: NTFYPriority = NTFYPriority.DEFAULT,
        tags: Optional[str] = None,
        click: Optional[str] = None,
        icon: Optional[HttpUrl] = None,
        url: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Optional[int]:
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
            Optional[int]: Código de estado HTTP si se envía, None en caso contrario.
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

        return await self.notifier.emit(payload=notification_payload)


    async def save_bcv_rates(self) -> None:
        """
        Fetch and persist all officially supported exchange rates from Banco Central de Venezuela.

        Iterates dynamically through the configured currency matrix, handling potential individual scraping or persistence anomalies defensively without interrupting the overall execution loop. Emits a consolidated notification metrics payload.

        Returns:
            None
        """
        self.logger.info("Starting batch synchronization for all active BCV currency assets...")
        updated_rates_summary: list[str] = []

        for cur in Currency.to_list():
            try:
                cur_save = await self.bcv_service.save_rate_to_db(cur)
                if not cur_save:
                    self.logger.error(f"Execution skipped for asset {cur.value}: Persistence routine returned invalid state.")
                    continue

                # Report construction
                msg = f"• {cur.value.upper()}: **{cur_save.rate:.3f} Bs/{cur.value}**"
                self.logger.info(f"Database sync successful for asset metric: {msg}")
                updated_rates_summary.append(msg)

            except DatabaseOperationError as e:
                err_msg = f"Database tracking constraint violation saving BCV token {cur.value}: {e}"
                self.logger.error(err_msg)
                await self._send_alert(
                    event="server_error",
                    title="Database Integrity Error",
                    description=err_msg,
                    priority=NTFYPriority.HIGH,
                    tags="rotating_light,skull",
                )
            except Exception as e:
                err_msg = f"Unhandled pipeline disruption isolating BCV token {cur.value}: {e}"
                self.logger.error(err_msg)
                await self._send_alert(
                    event="bcv_error",
                    title="BCV Request Exception",
                    description=err_msg,
                    priority=NTFYPriority.HIGH,
                    tags="rotating_light,skull",
                )

        if updated_rates_summary:
            consolidated_message = "Official Central Bank updates synchronized:\n" + "\n".join(updated_rates_summary)
            await self._send_alert(
                event="bcv_update",
                title="BCV Rates Batch Updated",
                description=consolidated_message,
                priority=NTFYPriority.DEFAULT,
                tags="bank,venezuela,chart_with_upwards_trend"
            )
            self.logger.info(f"BCV Rate succesfully saved: {len(updated_rates_summary)}")

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
            if not asset_fiat_buy or not asset_fiat_sell:
                self.logger.error(f"Some pairs can't be saved.")
                return False

            msg = f"Binance USDT/VES Updated: **{asset_fiat_buy.average_price:.3f} {currency.value}/{asset.value}** at Buy, **{asset_fiat_sell.average_price:.3f} {currency.value}/{asset.value}** at Sell"
            self.logger.info(msg)
            await self._send_alert(
                title="Binance USDT/VES Updated",
                event="binance_update",
                description=msg,
                priority=NTFYPriority.LOW,
                tags="rocket,chart_with_upwards_trend"
            )
            return True

        except DatabaseOperationError as e:
            err_msg = f"Dabasa operation error error saving Binance rates: {e}"
            self.logger.error(err_msg)
            await self._send_alert(
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

    def scheduler_jobs(self) -> None:
        """
        Dynamically registers execution rules driven by environmental variables parsed by Pydantic.
        """
        self.scheduler.add_job(
            self.save_bcv_rates,
            CronTrigger.from_crontab(self.config.BCV_CRON),
            id="bcv_rates_job"
        )
        self.logger.info(f"BCV successfully scheduled with cron {self.config.BCV_CRON}")

        self.scheduler.add_job(
            self.save_binance_ves_usdt_rate,
            CronTrigger.from_crontab(self.config.BINANCE_VES_CRON),
            id="binance_ves_job"
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

    async def shutdown(self) -> None:
        """Stop scheduler jobs and release owned resources."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
        await self.notifier.close()
