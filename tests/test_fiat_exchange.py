import logging
from app.services import FiatExchengeService

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s')

if __name__ == "__main__":
    fiat_service = FiatExchengeService()
    pair = fiat_service.get_pair(fiat_1="VES", fiat_2="PEN")
    for key, value in pair.model_dump().items():
        print(f"{key}: {value}")