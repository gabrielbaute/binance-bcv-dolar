from app.config import setup_logging
from app.services.binance_p2p import BinanceP2P

setup_logging()

if __name__ == "__main__":
    binance = BinanceP2P()
    price = binance.get_usdt_ves_pair()
    print(price)

