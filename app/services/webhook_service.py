import logging
import requests
from typing import Dict, Optional

from app.config import Config
from app.schemas import WebhookPayload

class NtfyWebhookService:
    """
    Service class to handle NTFY notifications asynchronously.
    """
    def __init__(self):
        """Initializes the Ntfy service with configuration."""
        self.topic = Config.NTFY_TOPIC
        self.base_url = Config.NTFY_URL
        self.webhook_url = f"{self.base_url.rstrip('/')}/{self.topic}"
        self.app_name = Config.APP_NAME
        self.app_version = Config.APP_VERSION
        self.logger = logging.getLogger(self.__class__.__name__)

    def _format_message(self, payload: WebhookPayload) -> str:
        """Formatear el mensaje para NTFY.
        
        Args:
            payload (WebhookPayload): Content of the notification.
        Returns:
            str: Message to send.
        """
        msg = f"[{payload.event}] {self.app_name} v{self.app_version} → {payload.description}"
        return msg

    def _format_headers(self, payload: WebhookPayload) -> Dict[str, str]:
        """Format the headers for NTFY.
        
        Args:
            payload (WebhookPayload): Content of the notification.
        Returns:
            Dict[str, str]: A dictionary with the headers.
        """
        headers = {
            "Priority": payload.priority.value,
            "Tags": payload.tags if payload.tags else "robot",
            "Topic": self.topic,
            "Markdown": "yes"
        }
        if payload.title:
            headers["Title"] = payload.title
        else:
            headers["Title"] = f"{self.app_name} - {payload.event}"
        if payload.tags:
            headers["Tags"] = payload.tags
        if payload.url:
            headers["Click"] = payload.url
        return headers

    def emit(self, payload: WebhookPayload) -> Optional[int]:
        """Emit a NTFY notification
        
        Args:
            payload (WebhookPayload): Notification content.
        Returns:
            Optional[int]: Status code of the notification.
        """
        message = self._format_message(payload)
        headers = self._format_headers(payload)
        try:
            response = requests.post(self.webhook_url, data=message.encode("utf-8"), headers=headers)
            response.raise_for_status()
            self.logger.debug(f"Ntfy notification sent successfully. Status code: {response.status_code}")
            return response.status_code
        except requests.RequestException as e:
            self.logger.error(f"Error sending Ntfy notification: {e}")
            return None