import logging
from app.services import BinanceP2P

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s')

if __name__ == "__main__":
    binance = BinanceP2P()
    price = binance.get_pair()
    for key, value in price.model_dump().items():
        print(f"{key}: {value}")

