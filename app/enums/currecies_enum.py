"""Lista de divisas soportadas por el BCV."""
from typing import List
from enum import StrEnum

class Currency(StrEnum):
    """
    Enum for representing currencies.

    Attributes:
        DOLAR (str): Represents the US Dollar.
        EURO (str): Represents the Euro.
        YUAN (str): Represents the Yuan.
        LIRA (str): Represents the Turkish Lira.
        RUBLE (str): Represents the Russian Ruble.
    """
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
        """
        Returns a description of the currency.

        Returns:
            str: A string describing the currency.
        """
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
    def to_list() -> List['Currency']:
        """
        Returns a list with all currencies suported.
        """
        currencies_list = [
            Currency.DOLAR,
            Currency.EURO,
            Currency.YUAN,
            Currency.LIRA,
            Currency.RUBLE
        ]

        return currencies_list
    
    @staticmethod
    def map_currency(str_currency: str) -> 'Currency':
        """
        Maps a strings expresion to a enum expresion.

        Args:
            str_currency(str): Currency in string.
        
        Returns:
            Currency: Currency in enum form.
        """
        currencies_map = {
            "dolar": Currency.DOLAR,
            "euro": Currency.EURO,
            "yuan": Currency.YUAN,
            "lira": Currency.LIRA,
            "rublo": Currency.RUBLE
        }
        try:
            return currencies_map.get(str_currency)
        except Exception:
            raise ValueError("Currency not suported.")