import logging
from app.services.binance_p2p import BinanceP2P

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s')

if __name__ == "__main__":
    binance = BinanceP2P()
    price = binance.get_usdt_ves_pair()
    print(price)

