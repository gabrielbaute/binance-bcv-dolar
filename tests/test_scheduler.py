from unittest.mock import AsyncMock, MagicMock

import pytest

from app.config import Config
from app.enums import BinanceAsset, FiatCurrency
from app.scheduler.dolar_scheduler import DolarScheduler


class TestDolarScheduler:
    @pytest.mark.asyncio
    async def test_save_currency_binance_rate_returns_false_when_a_pair_is_missing(self):
        scheduler = DolarScheduler(databasesession=MagicMock(), config=Config())
        sell_result = MagicMock(average_price=123.456)
        scheduler.binance_service.save_binance_currency = AsyncMock(
            side_effect=[None, sell_result]
        )
        scheduler._send_alert = AsyncMock()

        result = await scheduler.save_currency_binance_rate(
            currency=FiatCurrency.VES,
            asset=BinanceAsset.USDT,
        )

        assert result is False
        scheduler._send_alert.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_shutdown_stops_scheduler_and_closes_notifier(self):
        scheduler = DolarScheduler(databasesession=MagicMock(), config=Config())
        scheduler.scheduler = MagicMock()
        scheduler.scheduler.running = True
        scheduler.notifier.close = AsyncMock()

        await scheduler.shutdown()

        scheduler.scheduler.shutdown.assert_called_once_with(wait=False)
        scheduler.notifier.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_save_currency_binance_rate_returns_false_when_sell_pair_is_missing(self):
        scheduler = DolarScheduler(databasesession=MagicMock(), config=Config())
        buy_result = MagicMock(average_price=123.456)
        scheduler.binance_service.save_binance_currency = AsyncMock(
            side_effect=[buy_result, None]
        )
        scheduler._send_alert = AsyncMock()

        result = await scheduler.save_currency_binance_rate(
            currency=FiatCurrency.VES,
            asset=BinanceAsset.USDT,
        )

        assert result is False
        scheduler._send_alert.assert_not_awaited()
