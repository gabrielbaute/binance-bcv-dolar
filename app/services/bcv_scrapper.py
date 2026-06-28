"""BCV Scraper module."""

import logging
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Optional
from requests import Session, RequestException

from app.enums.currecies_enum import Currency
from app.errors.app_errors import BCVConnectionError
from app.schemas import BCVCurrencyResponse, BCVResponse

class BCVScraper:
    """Scraper for the BCV website that gets the exchange rates of different currencies."""

    def __init__(self):
        self.url = "https://www.bcv.org.ve"
        self.session = Session()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._soup = self._get_soup()

    def _get_soup(self) -> Optional[BeautifulSoup]:
        """
        Get and parse the HTML content from the BCV website.
        
        Returns:
            Optional[BeautifulSoup]: The parsed HTML content, or None if there was an error.
        
        Raises:
            BCVConnectionError: If there was an error connecting to the BCV website.
        """
        try:
            response = self.session.get(self.url, verify=False, timeout=15)
            response.raise_for_status()
            self.logger.info(f"Connected to {self.url}")
            return BeautifulSoup(response.text, "html.parser")
        except RequestException as e:
            self.logger.error(f"Error connecting to {self.url}: {e}")
            raise BCVConnectionError(
                details={"url": self.url, "error": str(e)}
            )
        except Exception as e:
            self.logger.error(f"Unexpected error while connecting to {self.url}: {e}")
            raise BCVConnectionError(
                message="Unexpected error while connecting to the BCV website.",
                details={"url": self.url, "error": str(e)}
            )

    def _get_currency_raw(self, currency: Currency) -> Optional[str]:
        """
        Get raw content for currency from the BCV page.

        Args:
            divisa (Currency): The currency to get the raw content for.

        Returns:
            Optional[str]: The raw content for the currency, or None if not found.
        """
        if not self._soup:
            return None

        div_container = self._soup.find("div", {"id": currency.currency()})
        if not div_container:
            self.logger.error(f"Currency container not found for {currency}")
            return None

        strong_tag = div_container.find("strong", {"class": "strong-tb"})
        if not strong_tag:
            valor_div = div_container.find("div", class_=lambda c: c and "centrado" in c)
            if not valor_div:
                self.logger.error(f"Exchange rate not found for {currency}")
                return None
            return valor_div.get_text(strip=True)

        return strong_tag.get_text(strip=True)

    def get_exchange_rate(self, currency: Currency) -> Optional[BCVCurrencyResponse]:
        """
        Returns the exchange rate for the given currency.

        Args:
            currency (Currency): The currency to get the exchange rate for.

        Returns:
            Optional[BCVCurrencyResponse]: The exchange rate for the currency, or None if not found.
        """
        raw_value = self._get_currency_raw(currency)
        if not raw_value:
            return None

        try:
            self.logger.info(f"Getting exchange rate for: {currency}")
            rate = float(raw_value.replace(",", "."))
            return BCVCurrencyResponse(
                currency=currency,
                rate=rate,
                date=datetime.now()
            )
        except ValueError:
            self.logger.error(f"Error parsing value '{raw_value}' for currency {currency}")
            return None

    def get_all_exchange_rates(self) -> BCVResponse:
        """
        Returns all the exchange rates for all the currencies.
        
        Returns:
            BCVResponse: The exchange rates for all the currencies.
        """
        dolar = self.get_exchange_rate(Currency.DOLAR)
        euro = self.get_exchange_rate(Currency.EURO)
        yuan = self.get_exchange_rate(Currency.YUAN)
        lira = self.get_exchange_rate(Currency.LIRA)
        rublo = self.get_exchange_rate(Currency.RUBLE)

        return BCVResponse(
            dolar=dolar,
            euro=euro,
            yuan=yuan,
            lira=lira,
            rublo=rublo
        )