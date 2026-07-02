"""
Tests for BCVController and BinanceController.

Uses an in-memory SQLite database (with SQLModel metadata) created in the
``db_session`` fixture from conftest.py.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.enums import Currency, TradeType, FiatCurrency, BinanceAsset
from app.schemas import BCVCurrencyCreate, BinanceCurrencyCreate
from app.controllers import BCVController, BinanceController


# ===================================================================
# BCVController
# ===================================================================

class TestBCVController:
    @pytest.mark.asyncio
    async def test_register_and_get_rate(self, db_session):
        controller = BCVController(session=db_session)

        created = await controller.register_rate(
            BCVCurrencyCreate(
                currency=Currency.DOLAR,
                trade_type=TradeType.SELL,
                rate=245.55,
                date=datetime.now(timezone.utc),
            )
        )
        assert created.rate == 245.55
        assert created.currency == Currency.DOLAR
        assert created.id is not None

        fetched = await controller.get_register_by_id(created.id)
        assert fetched.rate == 245.55

    @pytest.mark.asyncio
    async def test_get_last_register_by_currency(self, db_session):
        controller = BCVController(session=db_session)

        await controller.register_rate(
            BCVCurrencyCreate(
                currency=Currency.EURO,
                trade_type=TradeType.SELL,
                rate=260.0,
                date=datetime.now(timezone.utc),
            )
        )
        last = await controller.get_last_register_by_currency(Currency.EURO)
        assert last is not None
        assert last.rate == 260.0

    @pytest.mark.asyncio
    async def test_get_last_register_none(self, db_session):
        controller = BCVController(session=db_session)
        result = await controller.get_last_register_by_currency(Currency.YUAN)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_registers(self, db_session):
        controller = BCVController(session=db_session)

        for cur in [Currency.DOLAR, Currency.EURO]:
            await controller.register_rate(
                BCVCurrencyCreate(
                    currency=cur,
                    trade_type=TradeType.SELL,
                    rate=100.0,
                    date=datetime.now(timezone.utc),
                )
            )

        lst = await controller.get_registers_by_currency(
            currency=Currency.DOLAR, trade_type=TradeType.SELL
        )
        assert lst.count >= 1
        assert all(c.currency == Currency.DOLAR for c in lst.currencies)

    @pytest.mark.asyncio
    async def test_update_rate(self, db_session):
        controller = BCVController(session=db_session)
        created = await controller.register_rate(
            BCVCurrencyCreate(
                currency=Currency.DOLAR,
                trade_type=TradeType.SELL,
                rate=100.0,
                date=datetime.now(timezone.utc),
            )
        )
        updated = await controller.update_register_rate(
            created.id,
            BCVCurrencyCreate(
                currency=Currency.DOLAR,
                trade_type=TradeType.SELL,
                rate=200.0,
                date=datetime.now(timezone.utc),
            ),
        )
        assert updated.rate == 200.0

    @pytest.mark.asyncio
    async def test_delete_rate(self, db_session):
        controller = BCVController(session=db_session)
        created = await controller.register_rate(
            BCVCurrencyCreate(
                currency=Currency.DOLAR,
                trade_type=TradeType.SELL,
                rate=150.0,
                date=datetime.now(timezone.utc),
            )
        )
        deleted = await controller.delete_register_rate(created.id)
        assert deleted.id == created.id

        # Should now raise
        from app.errors import RegisterNotFoundError

        with pytest.raises(RegisterNotFoundError):
            await controller.get_register_by_id(created.id)

    @pytest.mark.asyncio
    async def test_get_registers_by_date_range(self, db_session):
        controller = BCVController(session=db_session)
        now = datetime.now(timezone.utc)

        await controller.register_rate(
            BCVCurrencyCreate(
                currency=Currency.DOLAR,
                trade_type=TradeType.SELL,
                rate=100.0,
                date=now,
            )
        )

        lst = await controller.get_registers_currency_by_date_range(
            currency=Currency.DOLAR,
            trade_type=TradeType.SELL,
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2030, 1, 1),
        )
        assert lst.count >= 1
        assert len(lst.currencies) >= 1

    @pytest.mark.asyncio
    async def test_get_registers_by_date_range_empty(self, db_session):
        controller = BCVController(session=db_session)
        lst = await controller.get_registers_currency_by_date_range(
            currency=Currency.DOLAR,
            trade_type=TradeType.SELL,
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2020, 1, 2),
        )
        assert lst.count == 0


# ===================================================================
# BinanceController
# ===================================================================

class TestBinanceController:
    @pytest.mark.asyncio
    async def test_register_and_get_rate(self, db_session):
        controller = BinanceController(session=db_session)
        created = await controller.register_rate(
            BinanceCurrencyCreate(
                fiat=FiatCurrency.VES,
                asset=BinanceAsset.USDT,
                trade_type=TradeType.BUY,
                average_price=346.97,
                median_price=347.00,
            )
        )
        assert created.average_price == 346.97
        assert created.fiat == FiatCurrency.VES

        fetched = await controller.get_register_by_id(created.id)
        assert fetched.average_price == 346.97

    @pytest.mark.asyncio
    async def test_get_last_register_by_pair(self, db_session):
        controller = BinanceController(session=db_session)

        await controller.register_rate(
            BinanceCurrencyCreate(
                fiat=FiatCurrency.VES,
                asset=BinanceAsset.USDT,
                trade_type=TradeType.BUY,
                average_price=350.0,
                median_price=349.0,
            )
        )
        last = await controller.get_last_register_by_pair(
            asset=BinanceAsset.USDT, fiat=FiatCurrency.VES, trade_type=TradeType.BUY
        )
        assert last is not None
        assert last.average_price == 350.0

    @pytest.mark.asyncio
    async def test_get_last_register_none(self, db_session):
        controller = BinanceController(session=db_session)
        result = await controller.get_last_register_by_pair(
            asset=BinanceAsset.USDT, fiat=FiatCurrency.PEN, trade_type=TradeType.BUY
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_get_registers_by_pair(self, db_session):
        controller = BinanceController(session=db_session)

        for tt in [TradeType.BUY, TradeType.SELL]:
            await controller.register_rate(
                BinanceCurrencyCreate(
                    fiat=FiatCurrency.VES,
                    asset=BinanceAsset.USDT,
                    trade_type=tt,
                    average_price=100.0,
                    median_price=99.0,
                )
            )

        result = await controller.get_registers_by_pair(
            asset=BinanceAsset.USDT, fiat=FiatCurrency.VES, trade_type=TradeType.BUY
        )
        assert result.count >= 1

    @pytest.mark.asyncio
    async def test_update_rate(self, db_session):
        controller = BinanceController(session=db_session)
        created = await controller.register_rate(
            BinanceCurrencyCreate(
                fiat=FiatCurrency.VES,
                asset=BinanceAsset.USDT,
                trade_type=TradeType.BUY,
                average_price=100.0,
                median_price=99.0,
            )
        )
        from app.schemas import BinanceCurrencyUpdate

        updated = await controller.update_register_rate(
            created.id,
            BinanceCurrencyUpdate(average_price=200.0),
        )
        assert updated.average_price == 200.0

    @pytest.mark.asyncio
    async def test_delete_rate(self, db_session):
        controller = BinanceController(session=db_session)
        created = await controller.register_rate(
            BinanceCurrencyCreate(
                fiat=FiatCurrency.VES,
                asset=BinanceAsset.USDT,
                trade_type=TradeType.BUY,
                average_price=150.0,
                median_price=149.0,
            )
        )
        deleted = await controller.delete_register_rate(created.id)
        assert deleted.id == created.id

        from app.errors import RegisterNotFoundError

        with pytest.raises(RegisterNotFoundError):
            await controller.get_register_by_id(created.id)