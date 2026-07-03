"""BCV Scraper module."""

import logging
from typing import Optional
from datetime import datetime
from bs4 import BeautifulSoup
from requests import Session, RequestException, ConnectTimeout
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import Currency, TradeType
from app.controllers import BCVController
from app.errors import (
    BCVConnectionError, 
    DatabaseSessionError,
    DatabaseOperationError, 
    BCVReadingRateError,
    RegisterNotFoundError
)
from app.schemas import (
    BCVCurrencyRealTimeResponse,
    BCVCurrencyListResponse,
    BCVCurrencyResponse, 
    BCVCurrencyCreate, 
    BCVCurrencyUpdate, 
    BCVResponse)

class BCVService:
    """
    Scraper for the BCV website that gets the exchange rates of different currencies.
    """
    def __init__(self, databasesession: Optional[AsyncSession] = None):
        self.url = "https://www.bcv.org.ve"
        self.request_session = Session()
        self.db_session = databasesession
        self.controller = BCVController(session=self.db_session) if self.db_session else None
        self.logger = logging.getLogger(self.__class__.__name__)
        self._soup: Optional[BeautifulSoup] = None

    def _get_soup(self) -> Optional[BeautifulSoup]:
        """
        Get and parse the HTML content from the BCV website.
        
        Returns:
            Optional[BeautifulSoup]: The parsed HTML content, or None if there was an error.
        
        Raises:
            BCVConnectionError: If there was an error connecting to the BCV website.
        """
        try:
            response = self.request_session.get(self.url, verify=False, timeout=15)
            response.raise_for_status()
            self.logger.info(f"Connected to {self.url}")
            return BeautifulSoup(response.text, "html.parser")
        except RequestException as e:
            self.logger.error(f"Error connecting to {self.url}: {e}")
            raise BCVConnectionError(
                message="Error connecting to the BCV website.",
                details={"url": self.url, "error": str(e)}
            )
        except ConnectTimeout as e:
            self.logger.error(f"Request time expired: {e}")
            raise BCVConnectionError(
                message="The request time out while attemp to connect.",
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
        self._soup = self._get_soup()
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

    def get_real_time_exchange_rate(self, currency: Currency) -> BCVCurrencyRealTimeResponse:
        """
        Returns the exchange rate for the given currency in real-time.

        Args:
            currency (Currency): The currency to get the exchange rate for.

        Returns:
            BCVCurrencyRealTimeResponse: The exchange rate for the currency.

        Raises:
            BCVReadingRateError: If the raw value cannot be converted to a float or if the currency is not found on the BCV website.
        """
        raw_value = self._get_currency_raw(currency)
        if not raw_value:
            raise BCVReadingRateError(
                message="Error reading the rate from the BCV website.",
                details={"currency": currency, "value": raw_value}
        )

        try:
            self.logger.info(f"Getting exchange rate for: {currency}")
            rate = float(raw_value.replace(",", "."))
            return BCVCurrencyRealTimeResponse(
                currency=currency,
                trade_type=TradeType.SELL,
                rate=rate,
                date=datetime.now()
            )
        except ValueError:
            self.logger.error(f"Error parsing value '{raw_value}' for currency {currency}")
            raise BCVReadingRateError(
                message="Error parsing the rate from the BCV website.",
                details={"currency": currency, "value": raw_value}
            )

    async def save_rate_to_db(self, currency: Currency) -> Optional[BCVCurrencyResponse]:
        """
        Save the exchange rate to the database.

        Args:
            currency (Currency): The currency for which to save the rate.

        Returns:
            Optional[BCVCurrencyResponse]: The saved exchange rate response, or None if there was an error.
        
        Raises:
            DatabaseSessionError: If the database session is not provided.
        """
        if not self.db_session:
            self.logger.error("Database session is not provided.")
            raise DatabaseSessionError(
                message="Database session is required to save rates.",
                details={"error": "No database session provided."}
            )
        
        currency_data = self.get_real_time_exchange_rate(currency=currency)

        new_rate = BCVCurrencyCreate(
            currency=currency_data.currency,
            trade_type=currency_data.trade_type,
            rate=currency_data.rate,
            date=currency_data.date
        )

        try:  
            saved_rate = await self.controller.register_rate(new_rate)
            return saved_rate
        except Exception as e:
            self.logger.error(f"Error saving rate to database: {e}")
            raise DatabaseOperationError(
                message="Error while saving currency record",
                details={"currency": currency, "error:": e}
            )

    async def get_exchange_rate(self, currency: Currency) -> Optional[BCVCurrencyResponse]:
        """
        Get the last exchange rate register for a specific currency.

        Args:
            currency (Currency): The currency to get the exchange rate for.
        
        Returns:
            Optional[BCVCurrencyResponse]: The exchange rate for the currency, or None if not found.
        
        Raises:
            DatabaseSessionError: If the database session is not provided.
            RegisterNotFoundError: If no exchange rate is found for the specified currency.
        """
        if not self.db_session:
            self.logger.error("Database session is not provided.")
            raise DatabaseSessionError(
                message="Database session is required to retrieve rates.",
                details={"error": "No database session provided."}
            )
        try:
            last_register = await self.controller.get_last_register_by_currency(currency=currency, trade_type=TradeType.SELL)
            if last_register is None:
                self.logger.warning(f"No exchange rate found for {currency}")
                raise RegisterNotFoundError(
                    message="No exchange rate found for the specified currency.",
                    details={"currency": currency}
                )
            return last_register
        except RegisterNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving exchange rate for {currency}: {e}")
            return None

    async def get_all_exchange_rates(self) -> BCVResponse:
        """
        Gets the last record registered for all the currencies tracked by BCV.
        
        Returns:
            BCVResponse: The exchange rates for all the currencies.
        
        Raises:
            DatabaseSessionError: If the database session is not provided.
        """
        if not self.db_session:
            self.logger.error("Database session is not provided.")
            raise DatabaseSessionError(
                message="Database session is required to retrieve rates.",
                details={"error": "No database session provided."}
            )
        
        dolar = await self.get_exchange_rate(Currency.DOLAR)
        euro = await self.get_exchange_rate(Currency.EURO)
        yuan = await self.get_exchange_rate(Currency.YUAN)
        lira = await self.get_exchange_rate(Currency.LIRA)
        rublo = await self.get_exchange_rate(Currency.RUBLE)

        return BCVResponse(
            dolar=dolar,
            euro=euro,
            yuan=yuan,
            lira=lira,
            rublo=rublo
        )
    
    async def get_currency_exchange_rates_by_range(
            self,
            start_date: datetime, 
            end_date: datetime,
            currency: Currency = Currency.DOLAR,
            trade_type: TradeType = TradeType.SELL,
            skip: int = 0,
            limit: int = 100
    ) -> BCVCurrencyListResponse:
        """
        Get all exchange rates registered between two dates.

        Args:
            start_date (datetime): The start date of the range.
            end_date (datetime): The end date of the range.
            currency (Currency): The currency to filter by. Defaults to Currency.DOLAR.
            trade_type (TradeType): The trade type to filter by. Defaults to TradeType.SELL.
            skip (int): The number of records to skip for pagination. Defaults to 0.
            limit (int): The maximum number of records to return. Defaults to 100.

        Returns:
            BCVCurrencyListResponse: A list of exchange rates and the total count.
        
        Raises:
            DatabaseSessionError: If the database session is not provided.
            RegisterNotFoundError: If no records are found for the specified criteria.
        """
        if not self.db_session:
            self.logger.error("Database session is not provided.")
            raise DatabaseSessionError(
                message="Database session is required to retrieve rates.",
                details={"error": "No database session provided."}
            )
        
        data = await self.controller.get_registers_currency_by_date_range(
            currency=currency,
            trade_type=trade_type,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )
        if data.count == 0:
            self.logger.warning(f"No records found for currency {currency} between {start_date} and {end_date}")
            raise RegisterNotFoundError(
                message="No records found for the specified currency and date range.",
                details={"currency": currency, "start_date": start_date, "end_date": end_date}
            )
        return data

    async def get_all_currency_registers(
            self, 
            currency: Currency, 
            trade_type: TradeType = TradeType.SELL,
            skip: int = 0,
            limit: int = 100
        ) -> BCVCurrencyListResponse:
        """
        Get all registers for a specific currency.

        Args:
            currency (Currency): The currency to filter by.
            trade_type (TradeType): The trade type to filter by. Defaults to TradeType.SELL.
            skip (int): The number of records to skip for pagination. Defaults to 0.
            limit (int): The maximum number of records to return. Defaults to 100.
        
        Returns:
            BCVCurrencyListResponse: A list of all registers for the specified currency.
        
        Raises:
            DatabaseSessionError: If the database session is not provided.
            RegisterNotFoundError: If no records are found for the specified currency.
        """
        if not self.db_session:
            self.logger.error("Database session is not provided.")
            raise DatabaseSessionError(
                message="Database session is required to retrieve rates.",
                details={"error": "No database session provided."}
            )
        
        data = await self.controller.get_registers_by_currency(
            currency=currency,
            trade_type=trade_type,
            skip=skip,
            limit=limit
        )
        if data.count == 0:
            self.logger.warning(f"No records found for currency {currency}")
            raise RegisterNotFoundError(
                message="No records found for the specified currency.",
                details={"currency": currency}
            )
        return data