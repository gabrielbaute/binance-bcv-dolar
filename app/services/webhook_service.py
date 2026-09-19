import logging
from typing import Dict, Optional
import httpx

from app.schemas import NTFYPayload
from app.config import Config

class NtfysService:
    """Servicio para emitir notificaciones a través de NTFY."""

    def __init__(self, config: Config, client: Optional[httpx.AsyncClient] = None) -> None:
        """Inicializa el servicio NTFY con la configuración y un cliente HTTP asíncrono.

        Args:
            settings (Settings): Instancia con la configuración general de la aplicación.
            client (Optional[httpx.AsyncClient]): Cliente asíncrono de HTTPX reutilizable.
        """
        self.config = config
        self.webhook_url = f"{self.config.NTFY_URL.rstrip('/')}/{self.config.NTFY_TOPIC}"
        self.app_name = config.APP_NAME
        self.app_version = config.APP_VERSION
        self.logger = logging.getLogger(self.__class__.__name__)
        self._client = client
        self._owns_client = client is None

    async def _get_client(self) -> httpx.AsyncClient:
        """Obtiene o crea un cliente HTTPX asíncrono.

        Returns:
            httpx.AsyncClient: Cliente de red asíncrono.
        """
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=10.0)
            self._owns_client = True
        return self._client

    def _format_message(self, payload: NTFYPayload) -> str:
        """Formatea el cuerpo del mensaje priorizando el contenido principal y firmando al final.

        Args:
            payload (NTFYPayload): Estructura de datos de la notificación.

        Returns:
            str: Mensaje formateado en Markdown.
        """
        body_parts = [payload.description]
        footer = f"— *{self.app_name}* `v{self.app_version}`"
        body_parts.append(footer)

        return "\n\n".join(body_parts)

    def _format_headers(self, payload: NTFYPayload) -> Dict[str, str]:
        """Genera los encabezados HTTP según las especificaciones de NTFY.

        Args:
            payload (NTFYPayload): Contenido de la notificación.

        Returns:
            Dict[str, str]: Diccionario con las cabeceras formateadas.
        """
        headers: Dict[str, str] = {
            "Priority": str(payload.priority.value),
            "Tags": payload.tags if payload.tags else "robot",
            "Markdown": "yes",
        }

        # El título en la cabecera es independiente del cuerpo
        if payload.title:
            headers["Title"] = payload.title
        elif payload.event:
            headers["Title"] = f"{self.app_name} - {payload.event}"
        else:
            headers["Title"] = self.app_name

        if payload.click:
            headers["Click"] = payload.click
        elif payload.url:
            headers["Click"] = payload.url

        if payload.icon:
            headers["Icon"] = str(payload.icon)

        return headers

    async def emit(self, payload: NTFYPayload) -> Optional[int]:
        """Emite una notificación a NTFY de forma asíncrona.

        Args:
            payload (NTFYPayload): Contenido estructurado de la notificación.

        Returns:
            Optional[int]: Código de estado HTTP retornado por el servidor NTFY.
        """
        message = self._format_message(payload)
        headers = self._format_headers(payload)
        client = await self._get_client()

        try:
            response = await client.post(
                self.webhook_url,
                content=message.encode("utf-8"),
                headers=headers,
            )
            response.raise_for_status()
            self.logger.debug(
                f"Notificación NTFY enviada exitosamente. Status code: {response.status_code}"
            )
            return response.status_code
        except httpx.HTTPError as e:
            self.logger.error(f"Error al enviar notificación NTFY: {e}")
            return None

    async def close(self) -> None:
        """Cierra el cliente HTTPX asíncrono si está activo."""
        if self._owns_client and self._client and not self._client.is_closed:
            await self._client.aclose()
