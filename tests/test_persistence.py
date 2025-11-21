from app.config import setup_logging
from app.database.db_config import init_db
from app.enums import Currency
from app.controllers.history_data_controller import HistoryDataController
from app.services.bcv_scrapper import BCVScraper
from app.services.binance_p2p import BinanceP2P

# Inicialización de logger y base de datos
setup_logging()
init_db()

# Controller
controller = HistoryDataController()

# Guardar BCV
scraper = BCVScraper()
bcv_response = scraper.get_exchange_rate(currency=Currency.DOLAR)
controller.save_bcv_rate(bcv_response)

# Guardar Binance
binance = BinanceP2P()
binance_response = binance.get_usdt_ves_pair()
controller.save_binance_rate(binance_response)
