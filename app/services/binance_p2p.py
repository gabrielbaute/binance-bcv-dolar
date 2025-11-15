import requests
import logging
from statistics import median
from typing import List, Optional
from app.schemas import BinanceRequest
   
class BinanceP2P:
    def __init__(self):
        self.url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        self.logger = logging.getLogger(f"[{self.__class__.__name__}]")


    def calculate_median_price(self, prices: List[float]) -> Optional[float]:
        """
        Calculate the median price.

        Args:
            prices (List[float]): List of prices.

        Returns:
            Optional[float]: Median price.
        """
        if prices:
            return median(prices)
        return None

    def calculate_average_price(self, prices: List[float]) -> float:
        """
        Calculate the average price.

        Args:
            prices (List[float]): List of prices.

        Returns:
            float: Average price.
        """
        if prices:
            return sum(prices) / len(prices)
        else:
            return None

    def build_request(
            self, 
            fiat: str, 
            page: Optional[int], 
            rows: Optional[int], 
            trade_type: Optional[str], 
            asset: Optional[str]
        ) -> BinanceRequest:
        """
        Build the body request for Binance P2P.

        Args:
            fiat (str): Fiat currency.
            page (Optional[int]): Page number.
            rows (Optional[int]): Number of rows per page.
            trade_type (Optional[str]): Trade type.
            asset (Optional[str]): Asset (USDT, BTC, etc).

        Returns:
            BinanceRequest: BinanceRequest object.
        """
        req = BinanceRequest(
            fiat=fiat,
            page=page,
            rows=rows,
            tradeType=trade_type,
            asset=asset
        )
        return req

    def do_request(self, req: BinanceRequest) -> dict:
        """
        Do the request to Binance P2P.

        Args:
            req (BinanceRequest): BinanceRequest object.

        Returns:
            dict: Response data.
        """
        body = req.model_dump()
        try:
            self.logger.info("Consultando Binance P2P")
            res = requests.post(self.url, json=body, headers={"accept": "application/json"})
            json_data = res.json()
            return json_data
        except Exception as e:
            self.logger.error(f"Error consultando Binance P2P: {e}")
            return None

    def colect_prices(self, data: dict) -> List[float]:
        """
        Colect prices from Binance P2P response.

        Args:
            data (dict): Response data.

        Returns:
            List[float]: List of prices.
        """
        if data.get("code") == "000000" and isinstance(data.get("data"), list) and len(data["data"]) > 0:
            precios = []
            for adv in data["data"]:
                precios.append(float(adv["adv"]["price"]))
            self.logger.info(f"Obteniendo {len(precios)} precios de Binance P2P")
            return precios
        else:
            print("Respuesta de Binance sin datos válidos:", data)
            return None
    
    def get_pair(self, fiat: str = "VES", asset: str = "USDT", trade_type: str = "BUY", rows: int = 20) -> Optional[float]:
        """
        Get the pair.

        Args:
            fiat (str, optional): Fiat currency. Defaults to "VES".
            asset (str, optional): Asset (USDT, BTC, etc). Defaults to "USDT".
            trade_type (str, optional): Trade type. Defaults to "BUY".
            rows (int, optional): Number of rows per page. Defaults to 20, max 20.

        Returns:
            Optional[float]: Pair.
        """
        body = self.build_request(fiat=fiat, page=1, rows=rows, trade_type=trade_type, asset=asset)
        data = self.do_request(body)
        if not data:
            return None
        precios = self.colect_prices(data)
        return self.calculate_average_price(precios)

    def get_usdt_ves_pair(self) -> float:
        """
        Get the USDT/VES pair.

        Returns:
            float: USDT/VES pair.
        """
        body = self.build_request(fiat="VES", page=1, rows=20, trade_type="BUY", asset="USDT")
        data = self.do_request(body)
        precios = self.colect_prices(data)
        promedio = self.calculate_average_price(precios)
        return promedio