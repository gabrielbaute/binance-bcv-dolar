import logging
from app.services import BCVScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s')

if __name__ == "__main__":
    bcv = BCVScraper()

    dolar_response = bcv.get_all_exchange_rates()
    dolar = dolar_response.dolar.rate
    euro = dolar_response.euro.rate
    yuan = dolar_response.yuan.rate
    lira = dolar_response.lira.rate
    rublo = dolar_response.rublo.rate

    print(f"Dolar: {dolar}")
    print(f"Euro: {euro}")
    print(f"Yuan: {yuan}")
    print(f"Lira: {lira}")
    print(f"Rublo: {rublo}")