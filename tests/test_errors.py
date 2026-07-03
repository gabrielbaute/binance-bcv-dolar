"""
Tests for custom error classes.
"""

from __future__ import annotations

import pytest
from app.errors import (
    DolarVzlaError,
    BCVConnectionError,
    BCVReadingRateError,
    RegisterNotFoundError,
    DatabaseSessionError,
    DatabaseOperationError,
    BinanceConnectionError,
    BinanceRequestError,
)


class TestDolarVzlaError:
    def test_base_error(self):
        err = DolarVzlaError("Something went wrong", {"key": "val"})
        assert err.message == "Something went wrong"
        assert err.details == {"key": "val"}
        assert str(err) == "Something went wrong"

    def test_base_error_default_details(self):
        err = DolarVzlaError("msg")
        assert err.details == {}


class TestBCVConnectionError:
    def test_default_message(self):
        err = BCVConnectionError()
        assert "BCV" in err.message
        assert err.details == {}

    def test_custom(self):
        err = BCVConnectionError("Custom", {"url": "https://bcv.org.ve"})
        assert err.message == "Custom"
        assert err.details["url"] == "https://bcv.org.ve"


class TestBCVReadingRateError:
    def test_default_message(self):
        err = BCVReadingRateError()
        assert "reading" in err.message.lower() or "rate" in err.message.lower()

    def test_custom(self):
        err = BCVReadingRateError("Bad parse", {"currency": "USD"})
        assert err.details["currency"] == "USD"


class TestRegisterNotFoundError:
    def test_default_message(self):
        err = RegisterNotFoundError()
        assert "not found" in err.message.lower()

    def test_is_dolar_vzla_error(self):
        assert issubclass(RegisterNotFoundError, DolarVzlaError)


class TestDatabaseSessionError:
    def test_default(self):
        err = DatabaseSessionError()
        assert "session" in err.message.lower()


class TestDatabaseOperationError:
    def test_default(self):
        err = DatabaseOperationError()
        assert "operation" in err.message.lower()


class TestBinanceConnectionError:
    def test_default(self):
        err = BinanceConnectionError()
        assert "Binance" in err.message


class TestBinanceRequestError:
    def test_default(self):
        err = BinanceRequestError()
        assert "request" in err.message.lower() or "Binance" in err.message


class TestErrorHierarchy:
    """All custom errors inherit from DolarVzlaError."""

    def test_bcv_connection(self):
        assert isinstance(BCVConnectionError(), DolarVzlaError)

    def test_bcv_reading(self):
        assert isinstance(BCVReadingRateError(), DolarVzlaError)

    def test_register_not_found(self):
        assert isinstance(RegisterNotFoundError(), DolarVzlaError)

    def test_database_session(self):
        assert isinstance(DatabaseSessionError(), DolarVzlaError)

    def test_database_operation(self):
        assert isinstance(DatabaseOperationError(), DolarVzlaError)

    def test_binance_connection(self):
        assert isinstance(BinanceConnectionError(), DolarVzlaError)

    def test_binance_request(self):
        assert isinstance(BinanceRequestError(), DolarVzlaError)