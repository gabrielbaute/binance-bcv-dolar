"""Binance P2P module."""
import requests
import logging
from statistics import median, mean
from typing import List, Optional, Dict

from app.schemas import BinanceRequest, BinanceResponse
   
class BinanceP2P:
    """
    Binance P2P Client.
    """
    def __init__(self):
        self.url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        self.logger = logging.getLogger(self.__class__.__name__)

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
        if rows > 20:
            raise ValueError("Rows must be less than or equal to 20")
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
            self.logger.debug("Request Binance P2P")
            res = requests.post(self.url, json=body, headers={"accept": "application/json"})
            json_data = res.json()
            return json_data
        except Exception as e:
            self.logger.error(f"Error at Binance P2P request: {e}")
            return None

    def colect_prices(self, data: dict, fiat: Optional[str] = None) -> List[float]:
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
            self.logger.info(f"Getting prices: {len(precios)} for {fiat}")
            return precios
        else:
            self.logger.error("Binance response error:", data)
            return None

    def calculate_med(self, prices: Optional[List[float]]) -> Dict[str, Optional[float]]:
        """
        Calculate the median price.

        Args:
            prices (list): List of prices.

        Returns:
            Dict[str, float]: Median and average price
        """
        if not prices:
            self.logger.warning("Empty price list received from Binance")
            return {"median_price": None, "average_price": None}
        try:
            median_price = median(prices)
            average_price = mean(prices)
            return {"median_price": median_price, "average_price": average_price}
        except Exception as e:
            self.logger.error(f"Error calculating median price: {e}")
            return {"median_price": None, "average_price": None}

    def get_pair(
            self, 
            fiat: str = "VES", 
            asset: str = "USDT", 
            trade_type: str = "BUY", 
            rows: int = 20
        ) -> Optional[BinanceResponse]:
        """
        Get the pair.

        Args:
            fiat (str, optional): Fiat currency. Defaults to "VES".
            asset (str, optional): Asset (USDT, BTC, etc). Defaults to "USDT".
            trade_type (str, optional): Trade type. Defaults to "BUY".
            rows (int, optional): Number of rows per page. Defaults to 20, max 20.

        Returns:
            Optional[BinanceResponse]: BinanceResponse object.
        """
        body = self.build_request(fiat=fiat, page=1, rows=rows, trade_type=trade_type, asset=asset)
        data = self.do_request(body)
        if not data:
            self.logger.warning("No data received from Binance")
            return None
        precios = self.colect_prices(data, fiat=fiat)
        medians = self.calculate_med(precios)
    
        pair = BinanceResponse(
            fiat=fiat,
            asset=asset,
            trade_type=trade_type,
            prices=precios,
            average_price=medians.get("average_price"),
            median_price=medians.get("median_price")
        )
        return pair

    def get_usdt_ves_pair(self) -> BinanceResponse:
        """
        Get the USDT/VES pair.

        Returns:
            BinanceResponse: USDT/VES pair data.
        """
        return self.get_pair(fiat="VES", asset="USDT", trade_type="BUY", rows=20)
        