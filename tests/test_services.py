from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.enums import BinanceAsset, Currency, FiatCurrency, TradeType
from app.errors import BinanceRequestError, DatabaseSessionError
from app.schemas import (
    BCVCurrencyRealTimeResponse,
    BinanceRealTimeResponse,
    BinanceRequest,
    NTFYPayload,
)
from app.services import (
    BCVService,
    BinanceService,
    FiatExchangeService,
    NtfyWebhookService,
    NtfysService,
)


def test_ntfy_webhook_service_compatibility_alias():
    assert NtfyWebhookService is NtfysService


@pytest.mark.asyncio
async def test_ntfy_service_reuses_injected_client_without_is_closed():
    class DummyConfig:
        NTFY_URL = "https://ntfy.example.com"
        NTFY_TOPIC = "test-topic"
        APP_NAME = "test-app"
        APP_VERSION = "1.0.0"

    class DummyClient:
        async def aclose(self):
            return None

    client = DummyClient()
    service = NtfysService(config=DummyConfig(), client=client)

    resolved_client = await service._get_client()

    assert resolved_client is client
    await service.close()
    assert service._client is None


def test_ntfy_service_omits_missing_event_in_fallback_title():
    class DummyConfig:
        NTFY_URL = "https://ntfy.example.com"
        NTFY_TOPIC = "test-topic"
        APP_NAME = "test-app"
        APP_VERSION = "1.0.0"

    service = NtfysService(config=DummyConfig())
    headers = service._format_headers(NTFYPayload(description="desc"))

    assert headers["Title"] == "test-app"


def test_bcv_service_uses_default_tls_verification(monkeypatch):
    captured_kwargs = {}

    class DummyClient:
        def __init__(self, **kwargs):
            captured_kwargs.update(kwargs)

    monkeypatch.setattr("app.services.bcv_service.AsyncClient", DummyClient)

    service = BCVService()
    service._get_client()

    assert "verify" not in captured_kwargs
    assert captured_kwargs["timeout"] == 15.0


@pytest.mark.asyncio
async def test_bcv_service_preserves_database_session_error():
    service = BCVService()
    service.get_real_time_exchange_rate = AsyncMock(
        return_value=BCVCurrencyRealTimeResponse(
            currency=Currency.DOLAR,
            trade_type=TradeType.SELL,
            rate=1.0,
            date=datetime.now(timezone.utc),
        )
    )

    with pytest.raises(DatabaseSessionError):
        await service.save_rate_to_db(Currency.DOLAR)


@pytest.mark.asyncio
async def test_binance_service_reuses_async_client(monkeypatch):
    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"code": "000000", "data": [{"adv": {"price": "1.0"}}]}

    class DummyClient:
        instances = 0

        def __init__(self, *args, **kwargs):
            type(self).instances += 1
            self.is_closed = False

        async def post(self, *args, **kwargs):
            return DummyResponse()

        async def aclose(self):
            self.is_closed = True

    monkeypatch.setattr("app.services.binance_service.AsyncClient", DummyClient)

    service = BinanceService()
    request = BinanceRequest(fiat="VES", tradeType="BUY", asset="USDT")

    await service._do_request(request)
    await service._do_request(request)

    assert DummyClient.instances == 1

    await service.close()
    assert service._client is None


@pytest.mark.parametrize("rows", [0, -1, 21])
def test_binance_service_rejects_invalid_row_counts(rows):
    service = BinanceService()

    with pytest.raises(
        BinanceRequestError,
        match="Rows parameter must be greater than 0 and no greater than 20.",
    ):
        service._build_request(
            fiat=FiatCurrency.VES,
            page=1,
            rows=rows,
            trade_type=TradeType.BUY,
            asset=BinanceAsset.USDT,
        )


@pytest.mark.asyncio
async def test_save_binance_currency_rejects_incomplete_pair():
    service = BinanceService()
    service.get_real_time_pair = AsyncMock(
        return_value=BinanceRealTimeResponse(
            fiat=FiatCurrency.VES,
            asset=BinanceAsset.USDT,
            trade_type=TradeType.BUY,
            prices=[],
            average_price=None,
            median_price=None,
        )
    )

    with pytest.raises(BinanceRequestError, match="Incomplete Binance pricing data"):
        await service.save_binance_currency(
            currency=FiatCurrency.VES,
            asset=BinanceAsset.USDT,
            trade_type=TradeType.BUY,
        )


@pytest.mark.asyncio
async def test_fiat_exchange_service_gets_real_time_pair():
    service = FiatExchangeService(database_session=None)
    service.binance.get_real_time_pair = AsyncMock(
        side_effect=[
            BinanceRealTimeResponse(
                fiat=FiatCurrency.VES,
                asset=BinanceAsset.USDT,
                trade_type=TradeType.BUY,
                average_price=100.0,
            ),
            BinanceRealTimeResponse(
                fiat=FiatCurrency.VES,
                asset=BinanceAsset.USDT,
                trade_type=TradeType.SELL,
                average_price=101.0,
            ),
            BinanceRealTimeResponse(
                fiat=FiatCurrency.PEN,
                asset=BinanceAsset.USDT,
                trade_type=TradeType.BUY,
                average_price=4.0,
            ),
            BinanceRealTimeResponse(
                fiat=FiatCurrency.PEN,
                asset=BinanceAsset.USDT,
                trade_type=TradeType.SELL,
                average_price=4.1,
            ),
        ]
    )

    pair = await service.get_real_time_pair(FiatCurrency.VES, FiatCurrency.PEN)

    assert pair.fiat_1_p2p_buy.average_price == 100.0
    assert pair.fiat_2_p2p_sell.average_price == 4.1
    assert pair.average_exchange_rate_f1_f2 == pytest.approx(0.041)
    assert pair.average_exchange_rate_f2_f1 == pytest.approx(25.25)
    assert service.binance.get_real_time_pair.await_count == 4
