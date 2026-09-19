from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from app.config import Config
from app.enums import NTFYPriority
from app.schemas import NTFYPayload
from app.services.webhook_service import NtfysService


class TestNtfysService:
    def test_format_headers_falls_back_to_app_name_without_event(self):
        service = NtfysService(config=Config())

        headers = service._format_headers(
            NTFYPayload(description="desc", priority=NTFYPriority.DEFAULT)
        )

        assert headers["Title"] == service.app_name

    @pytest.mark.asyncio
    async def test_close_skips_injected_client(self):
        client = AsyncMock()
        client.is_closed = False
        service = NtfysService(config=Config(), client=client)

        await service.close()

        client.aclose.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_close_closes_owned_client(self):
        client = AsyncMock()
        client.is_closed = False
        service = NtfysService(config=Config())
        service._client = client

        await service.close()

        client.aclose.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_emit_returns_status_code_on_success(self):
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status.return_value = None
        client = AsyncMock()
        client.post.return_value = response
        client.is_closed = False
        service = NtfysService(config=Config(), client=client)

        result = await service.emit(
            NTFYPayload(description="desc", priority=NTFYPriority.DEFAULT)
        )

        assert result == 200
        client.post.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_emit_returns_none_on_http_error(self):
        client = AsyncMock()
        client.post.side_effect = httpx.HTTPError("boom")
        client.is_closed = False
        service = NtfysService(config=Config(), client=client)

        result = await service.emit(
            NTFYPayload(description="desc", priority=NTFYPriority.DEFAULT)
        )

        assert result is None
