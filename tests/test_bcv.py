import logging
from app.services import BCVScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s')

if __name__ == "__main__":
    bcv = BCVScraper()

    dolar_response = bcv.get_all_exchange_rates()
    print(dolar_response.model_dump_json(indent=4))