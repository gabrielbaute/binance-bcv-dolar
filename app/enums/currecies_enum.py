"""Lista de divisas soportadas por el BCV."""

from enum import StrEnum

class Currency(StrEnum):
    """Enum for representing currencies."""
    DOLAR = "dolar"
    EURO = "euro"
    YUAN = "yuan"
    LIRA = "lira"
    RUBLE = "rublo"

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return f"Currency.{self.name}"
    
    @property
    def description(self) -> str:
        """Returns a description of the currency."""
        return {
            Currency.DOLAR: "Dólar estadounidense",
            Currency.EURO: "Euro",
            Currency.YUAN: "Yuan chino",
            Currency.LIRA: "Lira turca",
            Currency.RUBLE: "Rublo ruso"
        }.get(self, "Divisa desconocida")

    
    def currency_id(self) -> str:
        """Returns the currency ID in lowercase."""
        return self.name.lower()
    
    def currency(self) -> str:
        """Returns the currency name in lowercase."""
        return self.value.lower()
    
    @staticmethod
    def to_list() -> list:
        list = [
            Currency.DOLAR,
            Currency.EURO,
            Currency.YUAN,
            Currency.LIRA,
            Currency.RUBLE
        ]

        return list