from enum import Enum

class WebhookPriority(Enum):
    """
    Enum for NTFY priority levels.

    Attributes:
        max (str): Represents the maximum priority.
        high (str): Represents the high priority.
        default (str): Represents the default priority.
        low (str): Represents the low priority.
        min (str): Represents the minimum priority.
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