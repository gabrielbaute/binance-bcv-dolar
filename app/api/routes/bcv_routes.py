from fastapi import APIRouter, Query

from app.services import BCVScraper
from app.enums.currecies_enum import Currency
from app.schemas import BCVCurrencyResponse, BCVResponse

router = APIRouter(prefix="/bcv", tags=["BCV"])

@router.get("/realtime", response_model=BCVCurrencyResponse)
def realtime_bcv():
    scraper = BCVScraper()
    return {
        "dolar": scraper.get_exchange_rate(Currency.DOLAR),
        "euro": scraper.get_exchange_rate(Currency.EURO)
    }

@router.get("/dolar", response_model=BCVCurrencyResponse)
def dolar_bcv():
    scraper = BCVScraper()
    return scraper.get_exchange_rate(Currency.DOLAR)

@router.get("/euro", response_model=BCVCurrencyResponse)
def euro_bcv():
    scraper = BCVScraper()
    return scraper.get_exchange_rate(Currency.EURO)

@router.get("/all", response_model=BCVResponse)
def all_bcv():
    scraper = BCVScraper()
    return scraper.get_all_exchange_rates()

@router.get("/query", response_model=BCVResponse)
def query_bcv(
    currency: str = Query(..., description="Currency to query", enum=["dolar", "euro", "yuan", "lira", "rublo"])
    ):
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