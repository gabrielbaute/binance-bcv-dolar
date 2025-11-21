from enum import Enum

class WebhookPriority(Enum):
    """
    Enum for NTFY priority levels.
    """
    max = 'max'
    high = 'high'
    default = 'default'
    low = 'low'
    min = 'min'

    def __str__(self):
        return self.value

    @classmethod
    def has_value(cls, value: str) -> bool:
        return any(value == item.value for item in cls)

    @classmethod
    def list(cls) -> list:
        return list(map(lambda c: c.value, cls))