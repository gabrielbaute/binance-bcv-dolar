from typing import List
from enum import StrEnum

class FiatCurrency(StrEnum):
    """
    Enum for fiat currencies in Binance P2P.

    Attributes:
        VES (str): Venezuelan Bolívar.
        PEN (str): Peruvian Sol.
        USD (str): United States Dollar.
        USDT (str): Tether.
        EUR (str): Euro.
    """
    VES = "VES"
    PEN = "PEN"
    USD = "USD"
    USDT = "USDT"
    EUR = "EUR"

    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return self.value

    def currency(self) -> str:
        """Returns the currency name in lowercase."""
        return self.value.lower()
    
    @staticmethod
    def list_currencies() -> List[str]:
        """Returns the list of currencies avaiable."""
        return [currency.value for currency in FiatCurrency]
    
    @staticmethod
    def is_valid_currency(currency: str) -> bool:
        """Validate if the fiat currecy is avaiable."""
        return currency in FiatCurrency._value2member_map_
    
    @staticmethod
    def from_string(currency_str: str) -> 'FiatCurrency':
        """Validate the strings and returns an FiatCurrency object."""
        try:
            return FiatCurrency(currency_str)
        except ValueError:
            raise ValueError(f"Invalid currency: {currency_str}. Valid options are: {', '.join(FiatCurrency.list_currencies())}")