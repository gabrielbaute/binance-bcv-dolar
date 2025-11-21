from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

from app.enums import WebhookPriority

class WebhookPayload(BaseModel):
    """
    Schema for the payload to be sent via webhook.

    Attributes:
        title (Optional[str]): Title of the notification.
        event (str): The name of the event triggering the webhook.
        priority (WebhookPriority): Priority level of the notification.
        description (str): The main body content of the notification.
        tags (Optional[str]): Comma-separated tags or emojis (e.g., 'warning,skull').
        click (Optional[str]): URL to open when the notification is clicked.
        title (Optional[str]): Title of the notification.
        url (Optional[str]): Attachment URL or action URL.
        data (Optional[Dict[str, Any]]): Additional metadata or raw data.
    """
    title: Optional[str] = None
    event: str
    priority: WebhookPriority
    description: str
    tags: Optional[str] = None
    click: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Alerta de Arbitraje",
                    "event": "high_spread_alert",
                    "priority": "high",
                    "description": "El diferencial entre BCV y Binance supera el 5%.",
                    "tags": "warning,moneybag",
                    "title": "Alerta de Arbitraje",
                    "data": {"spread": 5.2, "bcv": 40.1, "binance": 42.3}
                }
            ]
        }
    )