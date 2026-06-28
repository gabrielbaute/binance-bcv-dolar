from app.config import setup_logging
from app.services.binance_p2p import BinanceP2P

setup_logging()

if __name__ == "__main__":
    binance = BinanceP2P()
    precios = binance.get_pair(fiat="PEN", asset="USDT", trade_type="BUY", rows=20)
    print(precios.model_dump_json(indent=7))

