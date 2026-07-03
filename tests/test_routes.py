"""
Integration-style tests for FastAPI route handlers.

All service-layer dependencies are mocked via ``conftest.py`` fixtures so that
no real HTTP requests or database queries are made.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.enums import (
    Currency,
    TradeType,
    FiatCurrency,
    BinanceAsset,
)
from app.schemas import (
    BinanceRealTimeResponse,
    BCVCurrencyResponse,
    BCVCurrencyRealTimeResponse,
    BCVCurrencyListResponse,
    BinanceCurrencyResponse,
    BinanceCurrencyListResponse,
    DolarResponse,
    FiatPairResponse,
)


# ===================================================================
# Helper to build common test objects
# ===================================================================

def _bcv_resp(rate=245.55) -> BCVCurrencyResponse:
    return BCVCurrencyResponse(
        id=uuid4(),
        currency=Currency.DOLAR,
        trade_type=TradeType.SELL,
        rate=rate,
        date=datetime.now(timezone.utc),
    )


def _bcv_rt_resp(rate=245.55) -> BCVCurrencyRealTimeResponse:
    return BCVCurrencyRealTimeResponse(
        currency=Currency.DOLAR,
        trade_type=TradeType.SELL,
        rate=rate,
        date=datetime.now(timezone.utc),
    )


def _binance_resp(avg=346.97) -> BinanceCurrencyResponse:
    return BinanceCurrencyResponse(
        id=uuid4(),
        fiat=FiatCurrency.VES,
        asset=BinanceAsset.USDT,
        trade_type=TradeType.BUY,
        average_price=avg,
        median_price=avg,
        date=datetime.now(timezone.utc),
    )


def _binance_rt_resp(avg=346.97) -> BinanceRealTimeResponse:
    return BinanceRealTimeResponse(
        fiat=FiatCurrency.VES,
        asset=BinanceAsset.USDT,
        trade_type=TradeType.BUY,
        average_price=avg,
        median_price=avg,
    )


# ===================================================================
#  /binance/…
# ===================================================================

class TestBinanceRoutes:
    async def test_realtime_ves(self, client, mock_binance_service):
        mock_binance_service.get_real_time_usdt_ves_pair.return_value = _binance_rt_resp()
        resp = await client.get("/binance/realtime_ves")
        assert resp.status_code == 200
        data = resp.json()
        assert data["average_price"] == 346.97
        assert data["fiat"] == "VES"

    async def test_realtime_pair(self, client, mock_binance_service):
        mock_binance_service.get_real_time_pair.return_value = _binance_rt_resp()
        resp = await client.get("/binance/real_time_pair?fiat=PEN&asset=USDT&trade_type=BUY")
        assert resp.status_code == 200

    async def test_ves_usdt_pair(self, client, mock_binance_service):
        mock_binance_service.get_last_saved_binance_fiat.side_effect = [
            _binance_resp(avg=345.0),
            _binance_resp(avg=344.0),
        ]
        resp = await client.get("/binance/ves_usdt_pair")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

    async def test_pair_last_record(self, client, mock_binance_service):
        mock_binance_service.get_last_saved_binance_fiat.side_effect = [
            _binance_resp(avg=350.0),
            _binance_resp(avg=349.0),
        ]
        resp = await client.get("/binance/pairs_last_record?fiat=VES&asset=USDT")
        assert resp.status_code == 200

    async def test_realtime_ves_failure_shows_error(self, client, mock_binance_service):
        mock_binance_service.get_real_time_usdt_ves_pair.return_value = None
        resp = await client.get("/binance/realtime_ves")
        # The handler returns None directly; FastAPI serialises it as null
        assert resp.status_code == 200
        assert resp.json() is None


# ===================================================================
#  /bcv/…
# ===================================================================

class TestBCVRoutes:
    async def test_realtime(self, client, mock_bcv_service):
        mock_bcv_service.get_real_time_exchange_rate.side_effect = [
            _bcv_rt_resp(rate=245.0),
            _bcv_rt_resp(rate=260.0),
        ]
        resp = await client.get("/bcv/realtime")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

    async def test_dolar(self, client, mock_bcv_service):
        mock_bcv_service.get_exchange_rate.return_value = _bcv_resp(rate=245.55)
        resp = await client.get("/bcv/dolar")
        assert resp.status_code == 200
        assert resp.json()["rate"] == 245.55

    async def test_euro(self, client, mock_bcv_service):
        mock_bcv_service.get_exchange_rate.return_value = _bcv_resp(rate=260.0)
        resp = await client.get("/bcv/euro")
        assert resp.status_code == 200
        assert resp.json()["rate"] == 260.0

    async def test_query(self, client, mock_bcv_service):
        mock_bcv_service.get_exchange_rate.return_value = _bcv_resp(rate=100.0)
        # Currency enum accepts lowercase values (e.g. "dolar")
        resp = await client.get("/bcv/query?currency=dolar")
        assert resp.status_code == 200


# ===================================================================
#  /dolar/…
# ===================================================================

class TestDolarRoutes:
    async def test_dolar_promedio(self, client, mock_dolar_service):
        mock_dolar_service.get_average_dolar_last_register.return_value = DolarResponse(
            bcv_dolar=_bcv_resp(rate=245.0),
            bcv_euro=_bcv_resp(rate=260.0),
            binance_usdt_ves_buy=_binance_resp(avg=346.0),
            average_usdt_ves=295.5,
            date=datetime.now(timezone.utc),
        )
        resp = await client.get("/dolar/dolar_promedio")
        assert resp.status_code == 200
        assert resp.json()["average_usdt_ves"] == 295.5


# ===================================================================
#  /history/…
# ===================================================================

class TestHistoryRoutes:
    async def test_bcv_history(self, client, mock_bcv_service):
        mock_bcv_service.get_currency_exchange_rates_by_range.return_value = (
            BCVCurrencyListResponse(currencies=[], count=0)
        )
        resp = await client.get(
            "/history/bcv?currency=dolar&start_date=2025-01-01T00:00:00&end_date=2025-12-31T00:00:00"
        )
        assert resp.status_code == 200
        assert resp.json()["count"] == 0

    async def test_bcv_history_no_dates(self, client, mock_bcv_service):
        mock_bcv_service.get_all_currency_registers.return_value = (
            BCVCurrencyListResponse(currencies=[_bcv_resp()], count=1)
        )
        resp = await client.get("/history/bcv?currency=dolar")
        assert resp.status_code == 200
        assert resp.json()["count"] == 1

    async def test_binance_history(self, client, mock_binance_service):
        mock_binance_service.get_binance_pair_by_time_range.return_value = (
            BinanceCurrencyListResponse(currencies=[], count=0)
        )
        resp = await client.get(
            "/history/binance?fiat=VES&asset=USDT&trade_type=BUY"
            "&start_date=2025-01-01&end_date=2025-12-31"
        )
        assert resp.status_code == 200

    async def test_binance_history_no_dates(self, client, mock_binance_service):
        mock_binance_service.get_all_saved_binance_pair.return_value = (
            BinanceCurrencyListResponse(currencies=[], count=0)
        )
        resp = await client.get("/history/binance?fiat=VES&asset=USDT&trade_type=BUY")
        assert resp.status_code == 200


# ===================================================================
#  /arbitrage/…
# ===================================================================

class TestFiatRoutes:
    async def test_pair(self, client, mock_fiat_exchange_service):
        mock_fiat_exchange_service.get_pair.return_value = FiatPairResponse(
            fiat_1_p2p_buy=_binance_resp(avg=346.0),
            fiat_1_p2p_sell=_binance_resp(avg=345.0),
            fiat_2_p2p_buy=_binance_resp(avg=3.75),
            fiat_2_p2p_sell=_binance_resp(avg=3.74),
            average_exchange_rate_f1_f2=0.0108,
            average_exchange_rate_f2_f1=92.5,
            date=datetime.now(timezone.utc),
        )
        resp = await client.get("/arbitrage/pair?fiat_1=VES&fiat_2=PEN")
        assert resp.status_code == 200
        assert resp.json()["average_exchange_rate_f1_f2"] == 0.0108

    async def test_real_time_pair(self, client, mock_fiat_exchange_service):
        mock_fiat_exchange_service.get_real_time_pair.return_value = FiatPairResponse(
            fiat_1_p2p_buy=_binance_rt_resp(avg=346.0),
            fiat_1_p2p_sell=_binance_rt_resp(avg=345.0),
            fiat_2_p2p_buy=_binance_rt_resp(avg=3.75),
            fiat_2_p2p_sell=_binance_rt_resp(avg=3.74),
            average_exchange_rate_f1_f2=0.0108,
            average_exchange_rate_f2_f1=92.5,
            date=datetime.now(timezone.utc),
        )
        resp = await client.get("/arbitrage/real_time_pair?fiat_1=VES&fiat_2=PEN")
        assert resp.status_code == 200

    async def test_fiat_historical(self, client, mock_fiat_exchange_service):
        mock_fiat_exchange_service.get_historical_pair.return_value = []
        resp = await client.get(
            "/history/fiat-pair?fiat_1=VES&fiat_2=PEN"
            "&start_date=2025-01-01&end_date=2025-12-31"
        )
        assert resp.status_code == 200