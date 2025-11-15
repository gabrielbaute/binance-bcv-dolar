import logging
from app.services.binance_p2p import BinanceP2P

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s')

if __name__ == "__main__":
    binance = BinanceP2P()
    body = binance.build_request(fiat="VES", page=1, rows=20, trade_type="BUY", asset="USDT")
    data = binance.do_request(body)
    precios = binance.colect_prices(data)
    promedio = binance.calculate_average_price(precios)
    print(precios)
    print(promedio)

