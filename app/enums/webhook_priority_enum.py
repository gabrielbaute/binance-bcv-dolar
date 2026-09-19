from enum import Enum, IntEnum
from typing import Union

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
    max = "max"
    high = "high"
    default = "default"
    low = "low"
    min = "min"

    def __str__(self):
        return self.value

    @classmethod
    def has_value(cls, value: str) -> bool:
        return any(value == item.value for item in cls)

    @classmethod
    def list(cls) -> list:
        return list(map(lambda c: c.value, cls))


class NTFYPriority(IntEnum):
    """Representa los niveles de prioridad de notificación para ntfy.

    Attributes:
        MAX (int): Prioridad máxima / urgente (ID: 5).
        HIGH (int): Prioridad alta (ID: 4).
        DEFAULT (int): Prioridad por defecto (ID: 3).
        LOW (int): Prioridad baja (ID: 2).
        MIN (int): Prioridad mínima (ID: 1).
    """

    MAX = 5
    HIGH = 4
    DEFAULT = 3
    LOW = 2
    MIN = 1

    @classmethod
    def has_value(cls, value: Union[int, str]) -> bool:
        """Identifica si un entero o cadena se corresponde con un valor del Enum.

        Args:
            value (Union[int, str]): Valor entero o texto a validar.

        Returns:
            bool: True si el valor es válido en el Enum, False en caso contrario.
        """
        try:
            cls.from_value(value)
            return True
        except ValueError:
            return False

    @classmethod
    def to_list(cls) -> list[int]:
        """Obtiene la lista completa de valores enteros del Enum.

        Returns:
            list[int]: Lista con los identificadores numéricos de prioridad.
        """
        return [item.value for item in cls]

    @classmethod
    def from_value(cls, value: Union[int, str]) -> "NTFYPriority":
        """Obtiene una instancia de NTFYPriority a partir de un entero o texto.

        Acepta enteros (1-5), cadenas con números ("5") o cadenas con los nombres
        oficiales de la documentación de ntfy ('max', 'urgent', 'high', 'default', 'low', 'min').

        Args:
            value (Union[int, str]): Identificador numérico o nombre de la prioridad.

        Returns:
            NTFYPriority: La instancia correspondiente del Enum.

        Raises:
            ValueError: Si el valor suministrado no coincide con ninguna prioridad.
        """
        if isinstance(value, int):
            return cls(value)

        if isinstance(value, str):
            clean_str = value.strip().lower()

            # Mapeo de nombres y alias indicados en la documentación
            name_mapping: dict[str, NTFYPriority] = {
                "max": cls.MAX,
                "urgent": cls.MAX,
                "high": cls.HIGH,
                "default": cls.DEFAULT,
                "low": cls.LOW,
                "min": cls.MIN,
            }

            if clean_str in name_mapping:
                return name_mapping[clean_str]

            # Intenta convertir cadenas numéricas como "5" o "1"
            if clean_str.isdigit():
                return cls(int(clean_str))

        raise ValueError(
            f"'{value}' no es un valor de prioridad válido para ntfy. "
            f"Valores permitidos: enteros {cls.to_list()}, cadenas numéricas equivalentes "
            f"como '5', o alias ('max', 'urgent', 'high', 'default', 'low', 'min')."
        )
