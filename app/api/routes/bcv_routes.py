from fastapi import APIRouter, Query

from app.services import BCVScraper
from app.enums.currecies_enum import Currency
from app.schemas import BCVCurrencyResponse, BCVResponse

router = APIRouter(prefix="/bcv", tags=["BCV"])

@router.get("/realtime", response_model=BCVCurrencyResponse)
def realtime_bcv():
    """
    The Euro/Dollar exchange rate for the day has been updated, according to the Central Bank of Venezuela (BCV).
    """
    scraper = BCVScraper()
    return {
        "dolar": scraper.get_exchange_rate(Currency.DOLAR),
        "euro": scraper.get_exchange_rate(Currency.EURO)
    }

@router.get("/dolar", response_model=BCVCurrencyResponse)
def dolar_bcv():
    """
    It provides the daily dollar exchange rate, according to the Central Bank of Venezuela (BCV). The daily rate is set the previous day, when banks close their exchange desks and report to the BCV, which publishes the average rate at 5 pm, Venezuelan time.
    """
    scraper = BCVScraper()
    return scraper.get_exchange_rate(Currency.DOLAR)

@router.get("/euro", response_model=BCVCurrencyResponse)
def euro_bcv():
    """
    It provides the daily euro exchange rate, according to the Central Bank of Venezuela (BCV). The daily rate is set the previous day, when banks close their exchange desks and report to the BCV, which publishes the average rate at 5 pm, Venezuelan time.
    """
    scraper = BCVScraper()
    return scraper.get_exchange_rate(Currency.EURO)

@router.get("/all", response_model=BCVResponse)
def all_bcv():
    """
    Returns the average exchange rate for the day for the five currencies registered by the BCV in the banking system: dolar, euro, yuan, lira and rublo.
    """
    scraper = BCVScraper()
    return scraper.get_all_exchange_rates()

@router.get("/query", response_model=BCVResponse)
def query_bcv(
    currency: str = Query(..., description="Currency to query", enum=["dolar", "euro", "yuan", "lira", "rublo"])
    ):
    """
    Returns the average echange rate for the day for the selected currency.
    """
    scraper = BCVScraper()
    currencies = {
        "dolar": Currency.DOLAR,
        "euro": Currency.EURO,
        "yuan": Currency.YUAN,
        "lira": Currency.LIRA,
        "rublo": Currency.RUBLE
    }
    currency = currencies.get(currency.lower())
    if not currency:
        return {
            "error": "Invalid currency",
            "message": "Currency must be one of the following: dolar, euro, yuan, lira, rublo"
            }
    return scraper.get_exchange_rate(currency)