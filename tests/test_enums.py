"""
Tests for enum modules: FiatCurrency, Currency, TradeType, BinanceAsset, NTFYPriority.
"""

from __future__ import annotations

import pytest
from app.enums import (
    FiatCurrency,
    Currency,
    TradeType,
    BinanceAsset,
    NTFYPriority,
)


# ===================================================================
# FiatCurrency
# ===================================================================

class TestFiatCurrency:
    def test_members(self):
        assert FiatCurrency.VES == "VES"
        assert FiatCurrency.PEN == "PEN"
        assert FiatCurrency.USD == "USD"
        assert FiatCurrency.USDT == "USDT"
        assert FiatCurrency.EUR == "EUR"

    def test_str(self):
        assert str(FiatCurrency.VES) == "VES"

    def test_repr(self):
        assert repr(FiatCurrency.VES) == "VES"

    def test_currency(self):
        assert FiatCurrency.VES.currency() == "ves"
        assert FiatCurrency.PEN.currency() == "pen"

    def test_list_currencies(self):
        lst = FiatCurrency.list_currencies()
        assert "VES" in lst
        assert "PEN" in lst
        assert len(lst) == 5

    def test_is_valid_currency(self):
        assert FiatCurrency.is_valid_currency("VES") is True
        assert FiatCurrency.is_valid_currency("XYZ") is False

    def test_from_string_valid(self):
        assert FiatCurrency.from_string("VES") == FiatCurrency.VES

    def test_from_string_invalid(self):
        with pytest.raises(ValueError, match="Invalid currency"):
            FiatCurrency.from_string("XYZ")


# ===================================================================
# Currency  (BCV)
# ===================================================================

class TestBCVCurrency:
    def test_members(self):
        assert Currency.DOLAR == "dolar"
        assert Currency.EURO == "euro"
        assert Currency.YUAN == "yuan"
        assert Currency.LIRA == "lira"
        assert Currency.RUBLE == "rublo"

    def test_str(self):
        assert str(Currency.DOLAR) == "dolar"

    def test_description(self):
        assert "Dólar" in Currency.DOLAR.description
        assert "Euro" in Currency.EURO.description

    def test_currency_id(self):
        assert Currency.DOLAR.currency_id() == "dolar"

    def test_currency_method(self):
        assert Currency.DOLAR.currency() == "dolar"


# ===================================================================
# TradeType
# ===================================================================

class TestTradeType:
    def test_members(self):
        assert TradeType.BUY == "BUY"
        assert TradeType.SELL == "SELL"

    def test_str(self):
        assert str(TradeType.BUY) == "BUY"

    def test_list_trades(self):
        lst = TradeType.list_trades()
        assert TradeType.BUY in lst
        assert TradeType.SELL in lst
        assert len(lst) == 2

    def test_is_valid_trade(self):
        assert TradeType.is_valid_trade("BUY") is True
        assert TradeType.is_valid_trade("HOLD") is False

    def test_from_string_valid(self):
        assert TradeType.from_string("SELL") == TradeType.SELL

    def test_from_string_invalid(self):
        with pytest.raises(ValueError, match="Invalid trade type"):
            TradeType.from_string("HOLD")


# ===================================================================
# BinanceAsset
# ===================================================================

class TestBinanceAsset:
    def test_members(self):
        assert BinanceAsset.USDT == "USDT"
        assert BinanceAsset.USDC == "USDC"
        assert BinanceAsset.DAI == "DAI"

    def test_str(self):
        assert str(BinanceAsset.USDT) == "USDT"

    def test_asset(self):
        assert BinanceAsset.USDT.asset() == "usdt"

    def test_list_currencies(self):
        lst = BinanceAsset.list_currencies()
        assert "USDT" in lst
        assert "USDC" in lst
        assert len(lst) == 3

    def test_is_valid_currency(self):
        assert BinanceAsset.is_valid_currency("USDT") is True
        assert BinanceAsset.is_valid_currency("BTC") is False

    def test_from_string_valid(self):
        assert BinanceAsset.from_string("USDC") == BinanceAsset.USDC

    def test_from_string_invalid(self):
        with pytest.raises(ValueError, match="Invalid asset"):
            BinanceAsset.from_string("BTC")


# ===================================================================
# NTFYPriority
# ===================================================================

class TestNTFYPriority:
    def test_members(self):
        assert NTFYPriority.MAX.value == 5
        assert NTFYPriority.HIGH.value == 4
        assert NTFYPriority.DEFAULT.value == 3
        assert NTFYPriority.LOW.value == 2
        assert NTFYPriority.MIN.value == 1

    def test_from_value(self):
        assert NTFYPriority.from_value(5) == NTFYPriority.MAX
        assert NTFYPriority.from_value("urgent") == NTFYPriority.MAX
        assert NTFYPriority.from_value("2") == NTFYPriority.LOW

    def test_has_value(self):
        assert NTFYPriority.has_value("high") is True
        assert NTFYPriority.has_value("urgent") is True
        assert NTFYPriority.has_value("critical") is False

    def test_to_list(self):
        lst = NTFYPriority.to_list()
        assert 5 in lst
        assert 1 in lst
        assert len(lst) == 5