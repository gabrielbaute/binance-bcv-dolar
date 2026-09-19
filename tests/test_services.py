from unittest.mock import AsyncMock

import pytest

from app.enums import BinanceAsset, FiatCurrency, TradeType
from app.errors import BinanceRequestError
from app.schemas import BinanceRealTimeResponse, BinanceRequest
from app.services import BCVService, BinanceService, NtfyWebhookService, NtfysService


def test_ntfy_webhook_service_compatibility_alias():
    assert NtfyWebhookService is NtfysService


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
    assert service._client.is_closed is True


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
