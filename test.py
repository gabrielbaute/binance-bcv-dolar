from app.config import setup_logging
from app.services.binance_p2p import BinanceP2P

setup_logging()

if __name__ == "__main__":
    binance = BinanceP2P()
    body = binance.build_request(fiat="VES", page=1, rows=20, trade_type="BUY", asset="USDT")
    data = binance.do_request(body)
    precios = binance.colect_prices(data)
    print(precios)

