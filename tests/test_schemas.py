"""
Tests for Pydantic response/request schemas.

We verify field presence, types, defaults, and serialization round-trips.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from app.enums import (
    Currency,
    TradeType,
    FiatCurrency,
    BinanceAsset,
    WebhookPriority,
)
from app.schemas import (
    BinanceRequest,
    BinanceRealTimeResponse,
    BinanceCurrencyResponse,
    BinanceCurrencyListResponse,
    BinanceCurrencyCreate,
    BinanceCurrencyUpdate,
    BCVCurrencyResponse,
    BCVCurrencyRealTimeResponse,
    BCVCurrencyListResponse,
    BCVResponse,
    BCVCurrencyCreate as BCVCurrencyCreateSchema,
    DolarResponse,
    RealTimeDolarResponse,
    FiatPairResponse,
    WebhookPayload,
)


# ===================================================================
# BinanceRequest
# ===================================================================

class TestBinanceRequest:
    def test_minimal(self):
        req = BinanceRequest(fiat="VES", tradeType="BUY", asset="USDT")
        assert req.fiat == "VES"
        assert req.page == 1

    def test_defaults(self):
        req = BinanceRequest(fiat="PEN", tradeType="SELL", asset="USDT")
        assert req.rows == 20
        assert req.filterType == "tradable"
        assert req.payTypes == []

    def test_serialization(self):
        req = BinanceRequest(fiat="VES", tradeType="BUY", asset="USDT")
        d = req.model_dump()
        assert d["fiat"] == "VES"
        assert d["page"] == 1


# ===================================================================
# BinanceRealTimeResponse
# ===================================================================

class TestBinanceRealTimeResponse:
    def test_full_data(self):
        r = BinanceRealTimeResponse(
            fiat=FiatCurrency.VES,
            asset=BinanceAsset.USDT,
            trade_type=TradeType.BUY,
            prices=[345.0, 346.0],
            average_price=345.5,
            median_price=345.5,
        )
        assert r.fiat == FiatCurrency.VES
        assert r.average_price == 345.5

    def test_empty_prices(self):
        r = BinanceRealTimeResponse(
            fiat=FiatCurrency.VES,
            asset=BinanceAsset.USDT,
            trade_type=TradeType.BUY,
        )
        assert r.prices is None
        assert r.average_price is None

    def test_serialization(self):
        r = BinanceRealTimeResponse(
            fiat=FiatCurrency.VES,
            asset=BinanceAsset.USDT,
            trade_type=TradeType.BUY,
        )
        d = r.model_dump()
        assert d["fiat"] == "VES"
        assert d["asset"] == "USDT"
        assert d["trade_type"] == "BUY"


# ===================================================================
# BinanceCurrencyResponse
# ===================================================================

class TestBinanceCurrencyResponse:
    def test_full(self, sample_binance_currency_dict):
        r = BinanceCurrencyResponse(**sample_binance_currency_dict)
        assert r.fiat == FiatCurrency.VES
        assert r.average_price == 346.97
        assert isinstance(r.id, UUID)

    def test_from_attributes(self, sample_binance_currency_dict):
        """from_attributes=True allows loading from a DB model."""
        r = BinanceCurrencyResponse.model_validate(sample_binance_currency_dict)
        assert r.average_price == 346.97

    def test_average_price_gt_zero(self):
        with pytest.raises(ValidationError):
            BinanceCurrencyResponse(
                id=uuid4(),
                fiat=FiatCurrency.VES,
                asset=BinanceAsset.USDT,
                trade_type=TradeType.BUY,
                average_price=-1,
                median_price=0,
                date=datetime.now(timezone.utc),
            )


# ===================================================================
# BinanceCurrencyCreate  /  Update
# ===================================================================

class TestBinanceCurrencyCreate:
    def test_valid(self):
        c = BinanceCurrencyCreate(
            fiat=FiatCurrency.VES,
            asset=BinanceAsset.USDT,
            trade_type=TradeType.BUY,
            average_price=350.0,
            median_price=349.0,
        )
        assert c.average_price == 350.0

    def test_average_price_must_be_positive(self):
        with pytest.raises(ValidationError):
            BinanceCurrencyCreate(
                average_price=-1, median_price=0, trade_type=TradeType.BUY,
            )


class TestBinanceCurrencyUpdate:
    def test_partial(self):
        u = BinanceCurrencyUpdate(average_price=355.0)
        assert u.average_price == 355.0
        assert u.fiat is None


# ===================================================================
# BinanceCurrencyListResponse
# ===================================================================

class TestBinanceCurrencyListResponse:
    def test_empty(self):
        lst = BinanceCurrencyListResponse(currencies=[], count=0)
        assert lst.count == 0
        assert lst.currencies == []


# ===================================================================
# BCVCurrencyResponse
# ===================================================================

class TestBCVCurrencyResponse:
    def test_full(self, sample_bcv_currency_dict):
        r = BCVCurrencyResponse(**sample_bcv_currency_dict)
        assert r.currency == Currency.DOLAR
        assert r.rate == 245.55
        assert r.trade_type == TradeType.SELL

    def test_default_trade_type(self, sample_bcv_currency_dict):
        sample_bcv_currency_dict.pop("trade_type")
        r = BCVCurrencyResponse(**sample_bcv_currency_dict)
        assert r.trade_type == TradeType.SELL


# ===================================================================
# BCVCurrencyRealTimeResponse
# ===================================================================

class TestBCVCurrencyRealTimeResponse:
    def test_valid(self):
        r = BCVCurrencyRealTimeResponse(
            currency=Currency.EURO, rate=260.12, date=datetime.now(timezone.utc)
        )
        assert r.currency == Currency.EURO
        assert r.trade_type == TradeType.SELL  # default


# ===================================================================
# BCVCurrencyListResponse
# ===================================================================

class TestBCVCurrencyListResponse:
    def test_empty(self):
        lst = BCVCurrencyListResponse()
        assert lst.count == 0
        assert lst.currencies == []

    def test_with_items(self, sample_bcv_currency_dict):
        item = BCVCurrencyResponse(**sample_bcv_currency_dict)
        lst = BCVCurrencyListResponse(currencies=[item], count=1)
        assert lst.count == 1


# ===================================================================
# BCVResponse
# ===================================================================

class TestBCVResponse:
    def test_all_none(self):
        r = BCVResponse(dolar=None, euro=None, yuan=None, lira=None, rublo=None)
        assert r.dolar is None

    def test_with_dolar(self, sample_bcv_currency_dict):
        d = BCVCurrencyResponse(**sample_bcv_currency_dict)
        r = BCVResponse(dolar=d, euro=None, yuan=None, lira=None, rublo=None)
        assert r.dolar.rate == 245.55


# ===================================================================
# DolarResponse
# ===================================================================

class TestDolarResponse:
    def test_minimal(self, sample_bcv_currency_dict, sample_binance_currency_dict):
        bcv = BCVCurrencyResponse(**sample_bcv_currency_dict)
        binance = BinanceCurrencyResponse(**sample_binance_currency_dict)
        r = DolarResponse(
            bcv_dolar=bcv,
            bcv_euro=None,
            binance_usdt_ves_buy=binance,
            average_usdt_ves=296.0,
            date=datetime.now(timezone.utc),
        )
        assert r.average_usdt_ves == 296.0
        assert r.bcv_dolar.rate == 245.55


# ===================================================================
# RealTimeDolarResponse
# ===================================================================

class TestRealTimeDolarResponse:
    def test_valid(self):
        r = RealTimeDolarResponse(
            bcv_dolar=BCVCurrencyRealTimeResponse(
                currency=Currency.DOLAR, rate=245.0, date=datetime.now(timezone.utc)
            ),
            bcv_euro=BCVCurrencyRealTimeResponse(
                currency=Currency.EURO, rate=260.0, date=datetime.now(timezone.utc)
            ),
            binance_usdt_ves_buy=BinanceRealTimeResponse(
                fiat=FiatCurrency.VES, asset=BinanceAsset.USDT, trade_type=TradeType.BUY
            ),
            average_usdt_ves=296.0,
            date=datetime.now(timezone.utc),
        )
        assert r.average_usdt_ves == 296.0


# ===================================================================
# WebhookPayload
# ===================================================================

class TestWebhookPayload:
    def test_minimal(self):
        p = WebhookPayload(event="test_event", priority=WebhookPriority.default, description="desc")
        assert p.event == "test_event"
        assert p.description == "desc"

    def test_optional_title(self):
        p = WebhookPayload(event="e", priority=WebhookPriority.high, description="d", title="My Title")
        assert p.title == "My Title"
